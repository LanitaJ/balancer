import sys
import requests
import json

url = 'http://127.0.0.1:8000/process_batch'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

cores = sys.argv[1]

data = {
    "data": [
        {
            "emotion": [
                "batch1"
            ],
            "transcription": [],
            "summarization": [
                "batch1"
            ]
        }
    ],
    "available_cores": cores
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print('Status Code:', response.status_code)
print('Response Text:', response.text)
