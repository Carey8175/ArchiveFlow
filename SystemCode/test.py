import requests
import torch


url = "http://127.0.0.1:18001/upload"
file_path = "/Users/carey/Code/Rag/SystemCode/core/天降神婿.txt"
kb_id = "test"

with open(file_path, 'rb') as f:
    files = {'file': f}
    data = {'kb_id': kb_id, 'user_id': 'carey'}
    response = requests.post(url, files=files, data=data)

try:
    print(response.json())
except requests.exceptions.JSONDecodeError:
    print("Response content is not in JSON format")
    print(response.text)