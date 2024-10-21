import logging
import threading
from SystemCode.server.model_manager import ModelManager
from SystemCode.configs.basic import LOG_LEVEL
from SystemCode.server.file_server.file_server import FileSystem


logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

model_manager = ModelManager()
logging.info("[Main] Starting System")

# start file System
logging.info("[Main] Model Manager started")
file_server = FileSystem(model_manager)
file_server_thread = threading.Thread(target=file_server.start)
file_server_thread.daemon = True
file_server_thread.start()
logging.info("[Main] File System started")