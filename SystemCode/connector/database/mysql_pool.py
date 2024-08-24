import logging
import pymysql

from queue import Queue
from threading import Lock, Thread
from SystemCode.configs.basic import LOG_LEVEL


# ----------------- Logger -----------------
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')


# ----------------- MySQL Thread Pool -----------------
class MySQLThreadPool:
    def __init__(self, max_connections, db_config):
        """
        初始化 MySQL 线程池
        :param max_connections: 线程池中最大连接数
        :param db_config: 数据库配置字典
        """
        self.max_connections = max_connections
        self.db_config = db_config
        self.pool = Queue(max_connections)
        self.lock = Lock()

        # 初始化连接池
        self._create_pool()

    def _create_pool(self):
        """
        创建连接池
        """
        for _ in range(self.max_connections):
            connection = pymysql.connect(**self.db_config)
            self.pool.put(connection)

    def get_connection(self):
        """
        从池中获取一个连接
        """
        with self.lock:
            if self.pool.empty():
                # 如果池中没有空闲连接，创建一个新的连接
                connection = pymysql.connect(**self.db_config)
                logging.warning('Mysql Pool Full, Create New Connection')
            else:
                connection = self.pool.get()
            return connection

    def release_connection(self, connection):
        """
        释放连接，将其返回池中
        """
        with self.lock:
            if connection.open:
                self.pool.put(connection)
            else:
                # 如果连接已关闭或失效，创建一个新的连接
                new_connection = pymysql.connect(**self.db_config)
                self.pool.put(new_connection)

    def close_all(self):
        """
        关闭池中所有的连接
        """
        with self.lock:
            while not self.pool.empty():
                connection = self.pool.get()
                connection.close()

