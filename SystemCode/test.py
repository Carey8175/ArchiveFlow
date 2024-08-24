import time
import pandas as pd
import pymysql
import random
import string
import uuid
import numpy as np
from datetime import datetime

# MySQL数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'orag'
}


def generate_random_string(length=10):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_vector(size=768):
    """生成随机向量"""
    return [random.random() for _ in range(size)]


def insert_batch(cursor, data_batch):
    """批量插入数据"""
    sql = """
    INSERT INTO Embedding (chunk_id, kb_id, file_id, timestamp, content, embedding)
    VALUES (%s, %s, %s, %s, %s, to_vector(%s))
    """
    cursor.executemany(sql, data_batch)


def main():
    # 创建数据库连接
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    kb_ids = [str(uuid.uuid4().hex) for _ in range(10)]

    sql = 'select vector_to_string(embedding) from Embedding where kb_id = "3d5a6795ddf8460dbb20de2f22772de9"'
    cursor.execute(sql)

    time1 = time.time()
    result = cursor.fetchall()

    df = pd.DataFrame(result, columns=['embedding'])
    df.map(lambda x: np.array(x))

    print(time.time() - time1)
    try:
        # 插入10万条数据，分批次每次1000条
        batch_size = 1000
        total_records = 100000
        for _ in range(total_records // batch_size):
            data_batch = []
            for _ in range(batch_size):
                chunk_id = uuid.uuid4().hex
                kb_id = random.choice(kb_ids)
                file_id = uuid.uuid4().hex
                timestamp = str(time.time())
                content = generate_random_string(4000)
                embedding = str(generate_random_vector(768))

                data = (
                    chunk_id,
                    kb_id,
                    file_id,
                    timestamp,
                    content,
                    embedding
                )
                data_batch.append(data)

            # 批量插入数据
            insert_batch(cursor, data_batch)
            # 提交事务
            connection.commit()
            print(f"Inserted {batch_size} records")

        print("Insertion complete")

    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()