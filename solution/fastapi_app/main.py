import datetime
import json
import logging
import multiprocessing
import os
import random
import time
from typing import List, Optional, Dict
from pydantic import BaseModel
import requests

import httpx
import uvicorn
from fastapi import FastAPI, Response
from opentelemetry.propagate import inject

from models.transcription import process as process_transcription
from models.summarizer import summarize_text as process_summarize_text
from models.emotionizer import analyze_emotion as process_analyze_emotion

from utils import PrometheusMiddleware, metrics, setting_otlp, \
        count_files, get_files, get_n_cores, send_to_storage

from common import EMOTION, TRANSCRIPTION, SUMMARIZATION, \
    DATA_PATH, \
    N_CORES_AVAILABLE, N_CORES_DEFAULT, \
    N_CORES_TRANSCRIPTION, N_CORES_EMOTION, N_CORES_SUMMARIZATION


# ALL ENVs TO COMMON:
APP_NAME = os.environ.get("APP_NAME", "app")
EXPOSE_PORT = os.environ.get("EXPOSE_PORT", 8000)
OTLP_GRPC_ENDPOINT = os.environ.get("OTLP_GRPC_ENDPOINT", "http://tempo:4317")

TARGET_ONE_HOST = os.environ.get("TARGET_ONE_HOST", "app-b")
TARGET_TWO_HOST = os.environ.get("TARGET_TWO_HOST", "app-c")

app = FastAPI()

# Setting metrics middleware
app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
app.add_route("/metrics", metrics)

# Setting OpenTelemetry exporter
setting_otlp(app, APP_NAME, OTLP_GRPC_ENDPOINT)


class EndpointFilter(logging.Filter):
    # Uvicorn endpoint access log filter
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


@app.get("/")
def read_root():
    logging.info("Hello World")
    r = random.randint(2, 5)
    time.sleep(r)
    requests.get("http://localhost:8000/cpu_task")
    return {"Hello": r}


def process_file(service_type, file_path):

    logging.info(f"PID:{os.getpid()} {datetime.datetime.now()} Processing {file_path} for {service_type}")

    func = {
        EMOTION :       process_analyze_emotion,
        TRANSCRIPTION : process_transcription,
        SUMMARIZATION : process_summarize_text,
    }

    result = func[service_type](file_path)

    logging.info(f"PID:{os.getpid()} {datetime.datetime.now()} Processed {file_path} for {service_type}")
    return result

def task_launcher(n_cores, service_type, files):
    logging.info(msg=f"{n_cores}, {service_type}, {len(files)}")
    results = -1
    try:
        with multiprocessing.Pool(n_cores) as pool:
            results = pool.starmap(process_file, [(service_type, file) for file in files])
    except ValueError as e:
        print(f'[ERROR]: {e}')
    return results


class TaskData(BaseModel):
    n_cores : int = 1
    files : List
    service_type: str

@app.post("/emotion")
def analyze_emotion(task: TaskData):
    logging.info(msg=f"{task.n_cores}, {task.service_type}, {len(task.files)}")
    return task_launcher(task.n_cores, task.service_type, task.files)

@app.post("/summarization")
def summarize_text(task: TaskData):
    logging.info(msg=f"{task.n_cores}, {task.service_type}, {len(task.files)}")
    return task_launcher(task.n_cores, task.service_type, task.files)

@app.post("/transcription")
def transcription(task: TaskData):
    logging.info(msg=f"{task.n_cores}, {task.service_type}, {len(task.files)}")
    return task_launcher(task.n_cores, task.service_type, task.files)


def run_in_parallel(task: Dict, all_files_count: int):
    service_type = task['service_type']
    files_count = task['files_count_for_type']
    folders = task["folders"]
    
    n_cores = get_n_cores(files_count, all_files_count)
    files = get_files(folders)
    
    logging.info(f"{n_cores}, {task}, {all_files_count}, {folders}")
    data = TaskData(
        n_cores=n_cores, 
        files=files,
        service_type=service_type
    )

    data_dict = data.dict()
    results = requests.post(f"http://localhost:8000/{service_type}", json=data_dict)

    return results




class Request(BaseModel):
    data: List[Dict] = [
                            {
                                "emotion" : ["batch2"],
                                "transcription" : ["going"],
                                "summarization" : ["batch1"]
                            }
                        ]
    available_cores: int = N_CORES_AVAILABLE

@app.post("/balancer")
def balancer(request: Request):
    events : List[Dict] = request.data

    results = {}

    for event in events:
        tasks: List[Dict] = []
        all_files_count = 0
        for service_type, folder_names in event.items():
            files_count_for_type = 0

            folders = []
            for folder_name in folder_names:
                if service_type == EMOTION:
                    folder = DATA_PATH + 'text/emotion/' + folder_name + '/'
                elif service_type == TRANSCRIPTION:
                    folder = DATA_PATH + 'audio/' + folder_name + '/'
                elif service_type == SUMMARIZATION:
                    folder = DATA_PATH + 'text/summarization/' + folder_name + '/'
                files_count_for_type += count_files(folder) 
                folders.append(folder)

            tasks.append({
                "service_type": service_type,
                "folders" : folders,
                "files_count_for_type" : files_count_for_type
            })
            all_files_count += files_count_for_type

    processes = []
    for task in tasks:
        p = multiprocessing.Process(target=run_in_parallel, args=(task, all_files_count, ))
        p.start()
        processes.append(p)

    # Wait for all processes to complete
    for process in processes:
        process.join()
        print(process)

    return results



@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    logging.error("items")
    return {"item_id": item_id, "q": q}


@app.get("/io_task")
async def io_task():
    time.sleep(1)
    logging.error("io task")
    return "IO bound task finish!"


@app.get("/cpu_task")
async def cpu_task():
    for i in range(1000):
        _ = i * i * i
    logging.info("cpu task")
    # requests.get("127.0.0.1:8000/cpu_task/new")
    return "CPU bound task finish!"


@app.get("/random_status")
async def random_status(response: Response):
    response.status_code = random.choice([200, 200, 300, 400, 500])
    logging.error("random status")
    return {"path": "/random_status"}


@app.get("/random_sleep")
async def random_sleep(response: Response):
    time.sleep(random.randint(0, 5))
    logging.error("random sleep")
    return {"path": "/random_sleep"}


@app.get("/error_test")
async def error_test(response: Response):
    logging.error("got error!!!!")
    raise ValueError("value error")


@app.get("/chain")
async def chain(response: Response):
    headers = {}
    inject(headers)  # inject trace info to header
    logging.critical(headers)

    async with httpx.AsyncClient() as client:
        await client.get(
            "http://localhost:8000/",
            headers=headers,
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_ONE_HOST}:8000/io_task",
            headers=headers,
        )
    async with httpx.AsyncClient() as client:
        await client.get(
            f"http://{TARGET_TWO_HOST}:8000/cpu_task",
            headers=headers,
        )
    logging.info("Chain Finished")
    return {"path": "/chain"}


if __name__ == "__main__":
    # update uvicorn access logger format
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"][
        "fmt"
    ] = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s"
    uvicorn.run(app, host="0.0.0.0", port=EXPOSE_PORT, log_config=log_config)
