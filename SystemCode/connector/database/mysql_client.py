import logging
import time
import uuid
import pymysql
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

        # self.conn_pool = MySQLThreadPool(MAX_CONNECTIONS, db_config=db_config)

    def get_conn(self):
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

        return conn

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

    def execute_query_(self, query, params, commit=False, fetch=False, many=False):
        # conn = self.conn_pool.get_connection()
        conn = self.get_conn()
        cursor = conn.cursor()

        if many:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)

        if commit:
            conn.commit()

        if fetch:
            result = cursor.fetchall()
        else:
            result = None

        cursor.close()
        # self.conn_pool.release_connection(conn)
        conn.close()
        logging.info("[SUCCESS] Query executed successfully with sql: {} \n".format(query))

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
                chunk_size INT DEFAULT -1,
                FOREIGN KEY (kb_id) REFERENCES KnowledgeBase(kb_id) ON DELETE CASCADE
            );

        """
        self.execute_query_(query, (), commit=True)

        # query = """
        #     CREATE TABLE Embedding (
        #         chunk_id VARCHAR(64),
        #         kb_id VARCHAR(255),
        #         file_id VARCHAR(64),
        #         timestamp VARCHAR(64),
        #         content TEXT,
        #         embedding TEXT,
        #         PRIMARY KEY (chunk_id, kb_id)
        #         )
        #     partition by key (kb_id)
        #     partitions 10;
        # """
        # self.execute_query_(query, (), commit=True)

    def insert_file(self, file_id, kb_id, file_name, file_path, status, file_size, docs):
        # table: File
        query = """
            INSERT INTO File (file_id, kb_id, file_name, file_path, status, timestamp, deleted, file_size, chunk_size)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        self.execute_query_(query, (file_id, kb_id, file_name, file_path, status, str(time.time()).split('.')[0], False, file_size, len(docs)), commit=True)

        # table: Embedding

        logging.info("[ SUCCESS ]File inserted successfully")

        return True

    def check_user_exist_(self, user_id):
        query = "SELECT user_id FROM User WHERE user_id = %s"
        result = self.execute_query_(query, (user_id,), fetch=True)
        logging.info("check_user_exist {}".format(result))
        return result is not None and len(result) > 0

    def check_user_exist_by_name(self, user_name):
        query = "SELECT user_name FROM User WHERE user_name = %s"
        result = self.execute_query_(query, (user_name,), fetch=True)
        logging.info("[check_user_exist_by_name] {}".format(result))
        return result is not None and len(result) > 0

    def add_user_(self, user_id, user_name=None):
        query = "INSERT INTO User (user_id, user_name) VALUES (%s, %s)"
        self.execute_query_(query, (user_id, user_name), commit=True)
        return user_id

    def create_milvus_collection(self, kb_id, user_id, kb_name, user_name=None):
        if not self.check_user_exist_(user_id):
            self.add_user_(user_id, user_name)
        query = "INSERT INTO KnowledgeBase (kb_id, user_id, kb_name) VALUES (%s, %s, %s)"
        self.execute_query_(query, (kb_id, user_id, kb_name), commit=True)
        return kb_id, "success"

    def placeholders(self, query, data):
        data = data if isinstance(data, list) else [data]
        placeholders = ','.join(['%s'] * len(data))
        return query.format(placeholders)

    def check_kb_exist(self, user_id, kb_ids) -> list:
        # 使用参数化查询
        query = "SELECT kb_id FROM KnowledgeBase WHERE kb_id IN ({}) AND deleted = 0 AND user_id = %s"
        query = self.placeholders(query, kb_ids)
        query_params = kb_ids + [user_id]
        result = self.execute_query_(query, query_params, fetch=True)
        logging.info("check_kb_exist {}".format(result))
        valid_kb_ids = [kb_info[0] for kb_info in result]
        unvalid_kb_ids = list(set(kb_ids) - set(valid_kb_ids))
        return unvalid_kb_ids

    def check_file_exist_by_name(self, user_id, kb_id, file_names):
        results = []
        batch_size = 100  # 根据实际情况调整批次大小

        # 分批处理file_names
        for i in range(0, len(file_names), batch_size):
            batch_file_names = file_names[i:i + batch_size]

            query = """
                SELECT file_id, file_name, file_size, status FROM File 
                WHERE deleted = 0
                AND file_name IN ({})
                AND kb_id = %s 
                AND kb_id IN (SELECT kb_id FROM KnowledgeBase WHERE user_id = %s)
            """
            query = self.placeholders(query, batch_file_names)
            query_params = batch_file_names + [kb_id, user_id]
            batch_result = self.execute_query_(query, query_params, fetch=True)
            logging.info("check_file_exist_by_name batch {}: {}".format(i // batch_size, batch_result))
            results.extend(batch_result)

        return results

    def add_file(self, user_id, kb_id, file_name, timestamp, file_size, file_path, status="waiting"):
        # 如果他传回来了一个id, 那就说明这个表里肯定有
        if not self.check_user_exist_(user_id):
            return None, "invalid user_id, please check..."
        not_exist_kb_ids = self.check_kb_exist(user_id, [kb_id])
        if not_exist_kb_ids:
            return None, f"invalid kb_id, please check {not_exist_kb_ids}"
        file_id = 'F'+ uuid.uuid4().hex
        query = "INSERT INTO File (file_id, kb_id, file_name, status, timestamp, file_size, file_path) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.execute_query_(query, (file_id, kb_id, file_name, status, timestamp, file_size, file_path), commit=True)
        logging.info("add_file: {}".format(file_id))
        return file_id, "success"

    def delete_knowledge_base(self, user_id, kb_id):
        query = "UPDATE KnowledgeBase SET deleted = 1 WHERE kb_id = %s AND user_id = %s"
        self.execute_query_(query, (kb_id, user_id), commit=True)
        return True

    def list_knowledge_base(self, user_id):
        query = "SELECT kb_id, kb_name FROM KnowledgeBase WHERE user_id = %s AND deleted = 0"
        result = self.execute_query_(query, (user_id,), fetch=True)
        return result

    def update_user_name(self, user_id, user_name, new_user_name):
        query = "UPDATE User SET user_name = %s WHERE user_id = %s AND user_name = %s"
        self.execute_query_(query, (new_user_name, user_id, user_name), commit=True, fetch=True)
        return True

    def match_user_name_and_id(self, user_id, user_name):
        query = "SELECT user_id FROM User WHERE user_id = %s AND user_name = %s"
        result = self.execute_query_(query, (user_id, user_name), fetch=True)
        return result

    def check_kb_exist_by_name(self, user_id, new_kb_name):
        query = "SELECT 1 FROM KnowledgeBase WHERE kb_name = %s AND user_id = %s"
        result = self.execute_query_(query, (new_kb_name, user_id), fetch=True)
        return bool(result)

    def update_knowledge_base_name(self, user_id, kb_id, new_kb_name):
        query = "UPDATE KnowledgeBase SET kb_name = %s WHERE kb_id = %s AND user_id = %s"
        self.execute_query_(query, (new_kb_name, kb_id, user_id), commit=True)
        return True

    #return file information include file_id, file_name, file_size, status, file_path, timestamp, chunk_size while deleted = 0
    def select_file_list_by_kb_id(self, kb_id):
        query = "SELECT * FROM File WHERE kb_id = %s AND deleted = 0"

        result = self.execute_query_(query, (kb_id, ), fetch=True)

        return result

    # def check_file_exist(self, user_id, kb_id, file_id):
    #     query = "SELECT 1 FROM File WHERE file_id = %s AND kb_id = %s AND kb_id IN (SELECT kb_id FROM KnowledgeBase WHERE user_id = %s)"
    #     result = self.execute_query_(query, (file_id, kb_id, user_id), fetch=True)
    #     return bool(result)

    def check_url_exist(self, kb_id, url):
        query = "SELECT 1 FROM File WHERE kb_id = %s AND file_path = %s"
        result = self.execute_query_(query, (kb_id, url), fetch=True)
        return bool(result)

    def delete_file(self, user_id, kb_id, file_id):
        query = "UPDATE File SET deleted = 1 WHERE file_id = %s AND kb_id = %s AND kb_id IN (SELECT kb_id FROM KnowledgeBase WHERE user_id = %s)"
        self.execute_query_(query, (file_id, kb_id, user_id), commit=True)
        return True




if __name__ == '__main__':
    client = MySQLClient('remote')
    client.check_kb_exist('1', ['1'])
