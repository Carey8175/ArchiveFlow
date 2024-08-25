import numpy as np
import pymysql
import pandas as pd
import faiss
from SystemCode.connector.database.mysql_client import MySQLClient

mysql_client = MySQLClient('remote')

# 从数据库中获取所有句子的向量
def get_embeddings_from_db():
    results = mysql_client.execute_query_('select content, embedding from Embedding limit 500', (), fetch=True)

    df = pd.DataFrame(results, columns=['content', 'embedding'])
    df['embedding'] = df['embedding'].apply(lambda x: np.fromstring(x, dtype='float32'))

    return df['content'].tolist(), np.stack(df['embedding'].values)


# 初始化 FAISS 索引
def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)  # 使用 L2 距离计算
    index.add(embeddings)  # 添加向量到索引
    return index


# 查找最相似的句子
# 获取数据
sentences, embeddings = get_embeddings_from_db()

# 初始化 FAISS 索引
dimension = embeddings.shape[1]  # 向量的维度
index = faiss.IndexFlatL2(dimension)  # 使用 L2 距离计算

# 将所有向量添加到索引中
index.add(embeddings)

# 假设我们有一个目标向量（768维）
target_vector = np.random.rand(768).astype('float32')  # 替换为实际的目标向量

# 查找与目标向量最相似的前 100 个向量
k = 100  # 需要找到的最近邻居数量
distances, indices = index.search(target_vector.reshape(1, -1), k)

# 输出结果
most_similar_sentences = [sentences[idx] for idx in indices[0]]
for sentence in most_similar_sentences:
    print(sentence)