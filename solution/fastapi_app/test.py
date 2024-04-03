from typing import List
from pydantic import BaseModel
import requests



class TaskData(BaseModel):
    n_cores : int = 1
    files : List
    service_type: str


    
service_type = "transcription"
# data = {
#         "n_cores" : 1, 
#         "files" : ['1', '2'],
#         "service_type" : service_type, 
# }

data = TaskData(
        n_cores=1, 
        files=['1', '2'],
        service_type=service_type
    )
print('DATA', data)

data_dict = data.dict()
print('DATA', data_dict)

# Use the json parameter to ensure data is correctly serialized to JSON
results = requests.post(f"http://localhost:8000/{service_type}", json=data_dict)
print(results.content)