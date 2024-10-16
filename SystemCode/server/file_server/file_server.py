import os
import logging
import time
import numpy as np
from BCEmbedding import EmbeddingModel

from SystemCode.connector.database import mysql_client, milvus_client
from SystemCode.configs.database import CONNECT_MODE


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    def __init__(self):
        self.mysql_client = mysql_client.MySQLClient(CONNECT_MODE)
        # Initialize the embedding model and move it to the GPU if available
        try:
            self.embed_model = EmbeddingModel(model_name_or_path=model_path)
        except Exception as e:
            logging.info("Failed to load model from local path, trying to load from Hugging Face")
            self.embed_model = EmbeddingModel(model_name_or_path=model_name)

    def embedding_file(self, docs) -> np.array:
        """ get the embedding result of the file"""
        docs_content = [doc.page_content for doc in docs]

        return self.embed_model.encode(docs_content)

    def start(self):
        """
        keep searching the file is not embedded and do the embedding
        :return:
        """
        while True:
            # get the file from the database

            # embed the file

            # save the embedding to the database

            time.sleep(FILE_SYSTEM_SLEEP_TIME)
