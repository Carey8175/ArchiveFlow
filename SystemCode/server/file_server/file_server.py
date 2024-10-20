import os
import logging
import time
from paddleocr import PaddleOCR

from SystemCode.core.file import File
from SystemCode.server.model_manager import ModelManager
from SystemCode.connector.database import mysql_client, milvus_client
from SystemCode.configs.database import CONNECT_MODE
from SystemCode.configs.basic import LOG_LEVEL


# ------------------ Logging ------------------
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', force=True)
logging.info("[File System] Start the file system.")
# ------------------ File System ------------------
# check the file is embedded or not every 5 seconds
FILE_SYSTEM_SLEEP_TIME = 5
current_file_path = os.path.abspath(__file__)
# 获取当前文件的父级文件夹
parent_directory = os.path.dirname(current_file_path)
# the content file path: SystemCode/content/User/knowledgeBase/single_file
content_file_path = os.path.join(os.path.dirname(parent_directory), "content")
model_path = os.path.join(parent_directory, "models", "bce-embedding-base_v1")
model_name = "maidalun1020/bce-embedding-base_v1"


class FileSystem:
    def __init__(self, model_manager: ModelManager):
        self.mysql_client = mysql_client.MySQLClient(CONNECT_MODE)
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, show_log=True)
        # Initialize the embedding model and move it to the GPU if available
        self.model_manager = model_manager

    def start(self):
        """
        keep searching the file is not embedded and do the embedding
        :return:
        """
        while True:
            # get the file from the database
            files_not_embedded = self.mysql_client.get_file_not_embedded()
            if not files_not_embedded:
                logging.info("No file needs to be embedded.")
                time.sleep(FILE_SYSTEM_SLEEP_TIME)
                continue

            for file in files_not_embedded:
                # embed the file
                if file[3].endswith(".url"):
                    the_file = File(file_id=file[0], kb_id=file[1], file_name=file[3], file_path=None, url=file[4])
                else:
                    the_file = File(file_id=file[0], kb_id=file[1], file_name=file[3], file_path=file[4])

                docs = the_file.split_file(self.ocr_engine)
                # docs = []
                if not docs:
                    self.mysql_client.update_status(
                        file_id=file[0],
                        status='error'
                    )
                    logging.error(f'[File System] Fail to split the file: {file[3]}')
                    continue

                embed = self.model_manager.get_embedding(docs)

                # save the embedding to the database
                milvus_client_ = milvus_client.MilvusClient(
                    user_id=file[2],
                    kb_ids=file[1],
                    mode=CONNECT_MODE
                )

                milvus_client_.insert_files_not_async(
                    file_id=file[0],
                    file_name=file[3],
                    file_path=file[4],
                    embs=embed,
                    docs=docs
                )
                logging.info('[File System] Insert into milvus successfully.')

                self.mysql_client.update_status_into_normal(
                    file_id=file[0],
                    chunk_size=len(docs)
                )

                logging.info('[File System] Update status in Mysql successfully.')

            time.sleep(FILE_SYSTEM_SLEEP_TIME)


if __name__ == '__main__':
    model_manager = ModelManager()
    file_system = FileSystem(model_manager)
    file_system.start()