import logging
import time
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# ------------------ File System ------------------
# check the file is embedded or not every 5 seconds
FILE_SYSTEM_SLEEP_TIME = 5


class FileSystem:
    def __init__(self):
        pass

    def embedding_file(self, docs) -> np.array:
        """ get the embedding result of the file"""

        return
        pass

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