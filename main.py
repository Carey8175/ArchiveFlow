import logging
import threading
import time

from SystemCode.server.file_server.file_server import FileSystem
from SystemCode.server.model_manager import ModelManager
from SystemCode.server.backends.sanic_api import app

logging.basicConfig(level=logging.INFO)
logging.info("[Main] Starting System")
print("[Main] Starting System")

# start file System
model_manager = ModelManager()
logging.info("[Main] Model Manager started")
print("[Main] Model Manager started")
file_server = FileSystem(model_manager)
file_server_thread = threading.Thread(target=file_server.start)
file_server_thread.daemon = True
file_server_thread.start()
logging.info("[Main] File System started")
print("[Main] File System started")


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=8777,
        access_log=False
    )
    logging.info("[Main] System started")
