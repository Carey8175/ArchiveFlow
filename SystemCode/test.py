import requests

url = "http://127.0.0.1:8777/api/orag/chat_stream"
data = {
    "user_id": "U3e6e0a3b608648e39cf8f9c37ec57c8f",
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "解释一下cnn 800字以上"}
    ]
}

response = requests.post(url, json=data, stream=True)

# 实时打印响应内容
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
        print()
