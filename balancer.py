import glob
from typing import Dict, List
import os
import tempfile
import multiprocessing
from werkzeug.utils import secure_filename
from pydantic import BaseModel, Field

from fastapi import FastAPI
from models.transcription import process as transcription
from models.summarizer import summarize_text
from models.cluster import process as clusterization
from models.emotionizer import analyze_emotion

app = FastAPI()

from common import EMOTION, TRANSCRIPTION, SUMMARIZATION, \
    BALANCER, BATCH_SIZE, \
    N_CORES_AVAILABLE, N_CORES_DEFAULT, \
    N_CORES_TRANSCRIPTION, N_CORES_EMOTION, N_CORES_SUMMARIZATION
    


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'wav'}

def process_file(service_type, file_path):
    print(f"PID:{os.getpid()}  Processing {file_path} for {service_type}")

    func = {
        EMOTION :       analyze_emotion,
        TRANSCRIPTION : transcription,
        SUMMARIZATION : summarize_text,
    }

    result = func[service_type](file_path)

    return f"PID:{os.getpid()}  Processed {file_path} for {service_type}"

def get_files(dir):
    full_path_files = []
    for batch in dir:
        full_path_files.extend(glob.glob(batch + "*")) 
    return full_path_files

def handle_service_batch(service_type, data_dir, n_cores):
    files = get_files(data_dir)
    # print(files)
    with multiprocessing.Pool(n_cores) as pool:
        results = pool.starmap(process_file, [(service_type, file) for file in files])
    return results




# DATA = [Batch1, Batch2, Batch3, ...]
# Batch = {
#           type1 : [dir_files1, dir_files2, ...],
#           type2 : [dir_files1, dir_files2, ...], 
#           ...
#         }

# {
#   "data": [        # print(batch)

#               {
#                   "emotion" : ["file1", "file2"],
#                   "transcription" : ["file3", "file4"],
#                   "summarization" : ["file4","file5", "file6"]
#               },
#               {
#                   "emotion" : ["file7", "file8"],
#                   "transcription" : ["file9", "file10"],
#                   "summarization" : ["file9","file10", "file11"]
#               },   
#            ]
# }
class Request(BaseModel):
    data: List[Dict] = [
                                {
                                    "emotion" : ["batch1", "batch2"],
                                    "transcription" : [],
                                    "summarization" : ["batch1", "batch2", "batch3", "batch4"]
                                }
                            ]
    available_cores: int = 8


def balancer_n_cores(tasks):
    return int((len(tasks) / BATCH_SIZE) * N_CORES_AVAILABLE)

def get_n_cores(batch):
    if BALANCER:
        return balancer_n_cores(batch)
    else:
        return N_CORES_DEFAULT

@app.post('/process_batch')
def process_batch(request: Request):
    batches : List[Dict] = request.data

    results = {}

    for batch in batches:
        for service_type, folder_names in batch.items():
            data_dir = []
            if service_type == TRANSCRIPTION: # временно
                continue
            print('---------------------------------------------------------------------------')
            # print(service_type, folder_names)

            for folder_name in folder_names:
                # сделать подпапки batch1, batch2, batchN чтобы подавать названия папок и парсить оттуда файлы, 
                # вместо подачи названий файлов 
                data_path = '/home/ygrigorev/Desktop/balancer/data/'
                if service_type == EMOTION:
                    folder = data_path + 'text/emotion/' + folder_name + '/'
                elif service_type == TRANSCRIPTION:
                    folder = data_path + 'audio/' + folder_name + '/'
                elif service_type == SUMMARIZATION:
                    folder = data_path + 'text/summarization/' + folder_name + '/'

                # file_path = os.path.join(folder, filename)
                # print(file_path)
            
                # print(file_paths)
                data_dir.append(folder)
            # print(data_dir)
            n_cores = get_n_cores(service_type)

            service_results = handle_service_batch(service_type, data_dir, n_cores)
            results[service_type] = service_results

    return {"results": results}


@app.get('/')
def main():
    return {"results": 'hello'}


# def main():
#     logging.info("Starting text clustering application.")


#     logging.info(f"Clustering completed. Result: {clusters}")



# https://kb.objectrocket.com/elasticsearch/build-an-elasticsearch-web-application-in-python-part-2-879
    
# ELK
# https://stackoverflow.com/questions/71320286/use-of-elk-with-python
# https://github.com/vklochan/python-logstash
# https://stackoverflow.com/questions/48195759/how-to-configure-native-python-logging-library-with-logstash-and-elastic


# Grafana
# https://grafana.com/docs/pyroscope/latest/configure-client/language-sdks/python/