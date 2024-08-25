import requests
import torch


url = "http://127.0.0.1:6006/upload"
file_path = "/tmp/pycharm_project_283/SystemCode/core/天降神婿.txt"
kb_id = "test1"

with open(file_path, 'rb') as f:
    files = {'file': f}
    data = {'kb_id': kb_id}
    response = requests.post(url, files=files, data=data)

try:
    print(response.json())
except requests.exceptions.JSONDecodeError:
    print("Response content is not in JSON format")
    print(response.text)