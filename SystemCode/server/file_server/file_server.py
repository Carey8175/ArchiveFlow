import os
import time
import uuid
import logging
import requests
import asyncio
import threading

from queue import Queue
from sanic import Sanic, response
from sanic.request import Request
from SystemCode.core.file import File
from BCEmbedding import EmbeddingModel
from SystemCode.connector.database.milvus_client import MilvusClient
from SystemCode.connector.database.mysql_client import MySQLClient
from SystemCode.configs.database import CONNECT_MODE
from SystemCode.configs.basic import FILE_SERVER_PORT, TASK_TIMEOUT


# ------------------ File Server ------------------
# route list
# /embedding: get embedding
# /embedding/<task_id>: get embedding status
# /upload: upload file
# /download: download file


def get_embedding():
    while True:
        if embedding_queue.empty():
            logging.debug('[FILE SERVER] Embedding queue is empty, waiting for embeddings')
            time.sleep(1)

        data = embedding_queue.get()
        task_id = data['task_id']
        sentences = data['sentences']

        # 更新任务状态为正在处理
        tasks[task_id]['status'] = 'processing'
        tasks[task_id]['progress'] = 0

        # Convert sentence to tensor and move to GPU
        try:
            embeddings = embed_model.encode(sentences)  # Assuming encode returns a list of embeddings
            tasks[task_id]['result'] = embeddings
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['completed_at'] = time.time()

        except Exception as e:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['error'] = str(e)
            tasks[task_id]['completed_at'] = time.time()


def clean_up_tasks():
    while True:
        current_time = time.time()
        tasks_to_delete = []

        for task_id, task_info in tasks.items():
            if task_info['status'] in ['completed', 'failed']:
                if task_info['completed_at'] and (current_time - task_info['completed_at'] > TASK_TIMEOUT):
                    tasks_to_delete.append(task_id)

        for task_id in tasks_to_delete:
            logging.info(f"Cleaning up task {task_id} due to timeout.")
            del tasks[task_id]

        time.sleep(60)  # 每60秒检查一次任务状态


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

file_server_app = Sanic("FileServer")
logging.info("File Server Starting")

current_file_path = os.path.abspath(__file__)
# 获取当前文件的父级文件夹
parent_directory = os.path.dirname(current_file_path)

# Directory to save uploaded files
UPLOAD_DIR = os.path.join(parent_directory, "content")
os.makedirs(UPLOAD_DIR, exist_ok=True)
model_path = os.path.join(parent_directory, "models", "bce-embedding-base_v1")
model_name = "maidalun1020/bce-embedding-base_v1"

# Initialize the embedding model and move it to the GPU if available
try:
    embed_model = EmbeddingModel(model_name_or_path=model_path)
except Exception as e:
    logging.info("Failed to load model from local path, trying to load from Hugging Face")
    embed_model = EmbeddingModel(model_name_or_path=model_name)

embedding_queue = Queue()
tasks = {}
logging.info("Embedding model loaded successfully")

# Initialize the MySQL client
mysql_client = MySQLClient(mode=CONNECT_MODE)
logging.info("MySQL client initialized successfully")

# Start the thread to extract embeddings
embedding_thread = threading.Thread(target=get_embedding)
clean_up_thread = threading.Thread(target=clean_up_tasks)
embedding_thread.start()
clean_up_thread.start()
logging.info("Embedding thread started successfully")


@file_server_app.route("/embedding", methods=["POST"])
async def embed_sentence(request: Request):
    # Extract the sentence from the request
    sentences = request.json.get('sentences')
    if not sentences:
        return response.json({"code": 101, "error": "No sentence provided"}, status=400)

    if not isinstance(sentences, list):
        return response.json({"code": 102, "error": "Sentences must be a list"}, status=400)

    # Get the embedding asynchronously
    task_id = uuid.uuid4().hex
    embedding_queue.put({"task_id": task_id, "sentences": sentences})
    tasks[task_id] = {
        'status': 'queued',
        'progress': 0,
        'result': None,
        'error': None,
        'created_at': time.time(),
        'completed_at': None
    }

    # Return the embedding as a JSON response
    return response.json({"code": 0, "data": {"task_id": task_id, 'queue': embedding_queue.qsize()}}, status=200)


@file_server_app.route("/embedding/<task_id>", methods=["GET"])
async def get_embedding_status(request: Request, task_id):
    task_info = tasks.get(task_id)
    if not task_info:
        return response.json({"code": 104, "error": "Task ID not found"}, status=404)

    if task_info['status'] == 'completed':
        embeddings = task_info['result'].tolist()
        # clean
        del tasks[task_id]
        return response.json({"code": 0, "status": "completed", "result": embeddings}, status=200)
    elif task_info['status'] == 'processing':
        return response.json({"code": 0, "status": "processing", "result": None}, status=200)
    elif task_info['status'] == 'queued':
        return response.json({"code": 0, "status": "queued", "result": None}, status=200)
    elif task_info['status'] == 'failed':
        return response.json({"code": 105, "status": "failed", "result": None, "error": task_info['error']}, status=500)


# Route to handle file uploads
@file_server_app.route("/upload", methods=["POST"])
async def upload_file(request: Request):
    # user_id, kb_id, file

    if not request.files:
        return response.json({"code": 1, "error": "No file provided"}, status=400)

    file = request.files.get('file')
    if 'kb_id' not in request.form:
        return response.json({"code": 2, "error": "kb_id not provided"}, status=400)
    kb_id = request.form.get('kb_id')

    if 'user_id' not in request.form:
        return response.json({"code": 2, "error": "user_id not provided"}, status=400)
    user_id = request.form.get('user_id')

    # Initialize the MilvusClient
    milvus_client = MilvusClient(mode=CONNECT_MODE,
                                 user_id=user_id,
                                 kb_ids=kb_id)
    logging.info("Milvus client initialized successfully")

    file_path = os.path.join(UPLOAD_DIR, file.name)

    with open(file_path, 'wb') as f:
        f.write(file.body)

    # embedding and insert to mysql
    file_id = uuid.uuid4().hex
    file = File(
        file_id=file_id,
        file_name=file.name,
        file_path=file_path,
        kb_id=kb_id,
    )

    logging.info('File id generated successfully: ' + file_id)
    docs = file.split_file(None)
    logging.info('File split successfully')

    # embedding request
    resp = requests.post(f"http://localhost:{FILE_SERVER_PORT}/embedding", json={"sentences": [doc.page_content for doc in docs]})
    if resp.status_code != 200:
        return response.json({"code": 3, "error": "Failed to get embeddings"}, status=500)

    logging.info('Embedding request sent successfully with task_id: ' + resp.json()['data']['task_id'])

    while tasks[resp.json()['data']['task_id']]['status'] != 'completed':
        logging.info('Waiting for embedding extraction to complete')
        await asyncio.sleep(1)

    embeddings = tasks[resp.json()['data']['task_id']]['result']
    logging.info('Embedding extracted successfully')

    status = mysql_client.insert_file(
        file_id=file_id,
        kb_id=kb_id,
        file_name=file.file_name,
        file_path=file_path,
        status='normal',
        file_size=os.path.getsize(file_path),
        docs=docs
    )

    status = await milvus_client.insert_files(
        file_id=file_id,
        file_name=file.file_name,
        file_path=file_path,
        docs=docs,
        embs=embeddings
    )

    if not status:
        return response.json({"code": 3, "error": "Failed to insert file to database"}, status=500)

    return response.json({"code": 0, "message": "File uploaded successfully"})


# Route to handle file downloads
@file_server_app.route("/download", methods=["POST"])
async def download_file(request: Request):
    # file_id = request.json.get('file_id')
    # if not file_id:
    #     return response.json({"code": 201, "error": "file_id not provided"}, status=400)
    #
    # file_path = os.path.join(UPLOAD_DIR, file_id)
    #
    # if not os.path.exists(file_path):
    #     return response.json({"error": "File not found"}, status=404)
    #
    # return await response.file(file_path)
    pass


if __name__ == "__main__":
    file_server_app.run(host="127.0.0.1", port=FILE_SERVER_PORT, debug=True)
