import logging
import pymysql

from mysql_pool import MySQLThreadPool
from SystemCode.configs.database import *
from SystemCode.configs.basic import LOG_LEVEL

# ----------------- Logger -----------------
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')


# ----------------- MySQL Client -----------------
class MySQLClient:
    def __init__(self, mode):
        if mode == 'local':
            self.host = MYSQL_LOCAL_HOST
        else:
            self.host = MYSQL_REMOTE_HOST
        self.port = MYSQL_PORT
        self.user = MYSQL_USER
        self.password = MYSQL_PASSWORD
        self.database = MYSQL_DATABASE
        self._check_connection()

        db_config = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
        }

        self.conn_pool = MySQLThreadPool(MAX_CONNECTIONS, db_config=db_config)

    def _check_connection(self):
        # connect to mysql
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password
        )

        cursor = conn.cursor()
        cursor.execute('SHOW DATABASES')
        databases = [database[0] for database in cursor]

        if self.database not in databases:
            # 如果数据库不存在，则新建数据库
            cursor.execute('CREATE DATABASE IF NOT EXISTS {}'.format(self.database))
            logging.debug("数据库{}新建成功或已存在".format(self.database))
        logging.info("[SUCCESS] 数据库{}检查通过".format(self.database))

        cursor.close()
        conn.close()

    def execute_query_(self, query, params, commit=False, fetch=False):
        conn = self.conn_pool.get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute(query, params)

        if commit:
            conn.commit()

        if fetch:
            result = cursor.fetchall()
        else:
            result = None

        cursor.close()
        self.conn_pool.release_connection(conn)

        return result

    def create_tables_(self):
        query = """
            CREATE TABLE IF NOT EXISTS User (
                user_id VARCHAR(255) PRIMARY KEY,
                user_name VARCHAR(255)
            );
        """

        self.execute_query_(query, (), commit=True)
        query = """
            CREATE TABLE IF NOT EXISTS KnowledgeBase (
                kb_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255),
                kb_name VARCHAR(255),
                deleted BOOL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
            );

        """
        self.execute_query_(query, (), commit=True)

        query = """
            CREATE TABLE IF NOT EXISTS File (
                file_id VARCHAR(255) PRIMARY KEY,
                kb_id VARCHAR(255),
                file_name VARCHAR(255),
                file_path VARCHAR(255),
                status VARCHAR(255),
                timestamp VARCHAR(255),
                deleted BOOL DEFAULT 0,
                file_size INT DEFAULT -1,
                content_length INT DEFAULT -1,
                chunk_size INT DEFAULT -1,
                FOREIGN KEY (kb_id) REFERENCES KnowledgeBase(kb_id) ON DELETE CASCADE
            );

        """
        self.execute_query_(query, (), commit=True)

        query = """
            CREATE TABLE Embedding (
                chunk_id VARCHAR(64),
                kb_id VARCHAR(255),
                file_id VARCHAR(64),
                timestamp VARCHAR(64),
                content VARCHAR(4000),
                embedding VECTOR(768),
                PRIMARY KEY (chunk_id, kb_id)
                )
            partition by key (kb_id)
            partitions 10;
        """
        self.execute_query_(query, (), commit=True)
