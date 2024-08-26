import os
import asyncio
import uuid
import logging

from sanic import Sanic, response
from sanic.request import Request
from SystemCode.core.file import File
from BCEmbedding import EmbeddingModel
from SystemCode.connector.database.mysql_client import MySQLClient
from SystemCode.configs.database import CONNECT_MODE

# ------------------ File Server ------------------
# route list
# /embed: get embedding
# /upload: upload file
# /download: download file

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

logging.info("Embedding model loaded successfully")

# Initialize the MySQL client
mysql_client = MySQLClient(mode=CONNECT_MODE)
logging.info("MySQL client initialized successfully")


# Route to handle file uploads
@app.route("/upload", methods=["POST"])
async def upload_file(request: Request):
    if not request.files:
        return response.json({"code": 1, "error": "No file provided"}, status=400)

    file = request.files.get('file')
    if 'kb_id' not in request.form:
        return response.json({"code": 2, "error": "kb_id not provided"}, status=400)
    kb_id = request.form.get('kb_id')

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

    docs = file.split_file(None)

    # Get the embedding asynchronously
    embeddings = embed_model.encode([doc.page_content for doc in docs])

    status = mysql_client.insert_file(
        file_id=file_id,
        kb_id=kb_id,
        file_name=file.file_name,
        file_path=file_path,
        status='normal',
        file_size=os.path.getsize(file_path),
        docs=docs,
        embeddings=embeddings.tolist()
    )

    if not status:
        return response.json({"code": 3, "error": "Failed to insert file to database"}, status=500)

    return response.json({"code": 0, "message": "File uploaded successfully"})


# Route to handle file downloads
@app.route("/download", methods=["POST"])
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
    file_server_app.run(host="127.0.0.1", port=6006, single_process=True, debug=True)