import pymilvus
from pymilvus import connections, list_collections, Collection, FieldSchema, DataType, CollectionSchema


def connect_to_milvus(host='47.108.135.173', port='19530'):
    # 连接到自定义的 Milvus 实例
    connections.connect(alias='default', host=host, port=port)


def list_collections_in_milvus():
    # 列出所有集合
    collections = list_collections()
    return collections


def create_new_collection(collection_name):
    # 定义集合中的字段
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),  # 主键字段
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),  # 向量字段，128维
    ]

    # 定义集合的schema
    schema = CollectionSchema(fields=fields, description="Example collection")

    # 创建新的集合
    collection = Collection(name=collection_name, schema=schema)

    return f"Collection '{collection_name}' created successfully."


def describe_collection(collection_name):
    # 获取指定集合的对象
    collection = Collection(collection_name)

    # 返回集合的描述信息（如字段等）
    schema_info = collection.schema
    # 获取集合的统计信息
    stats = collection.num_entities

    return {
        "schema_info": schema_info,
        "number_of_entities": stats
    }


if __name__ == '__main__':
    from SystemCode.connector.database.mysql_client import MySQLClient

    mysql_client = MySQLClient('remote')
    mysql_client.update_user_name(
        user_id='Uf359e0df1eac498e91b3adaeb986ba0c',
        user_name='holyshit',
        new_user_name='holyshit2'
    )

    connect_to_milvus()
    collections_ = list_collections_in_milvus()
    print(collections_)
    print(describe_collection('c89149173e4b435cbf0f5be4302086c4'))
    # Collection('c89149173e4b435cbf0f5be4302086c4').drop()


    from BCEmbedding import EmbeddingModel
    from SystemCode.connector.database.milvus_client import MilvusClient
    #
    model = EmbeddingModel()
    query = 'ISS'

    # Get the embeddings for the query
    embedding = model.encode(query)
    #
    my = MilvusClient(mode='remote', user_id='c89149173e4b435cbf0f5be4302086c4', kb_ids='KB2c83eb356644492cbadd36a176e8b7f3')
    partition = pymilvus.Partition(my.sess, 'KB2c83eb356644492cbadd36a176e8b7f3')
    print(partition.num_entities)

    # print('partition: ', my.sess.partitions)
    # if my.sess.has_partition('KB2c83eb356644492cbadd36a176e8b7f3'):
    #     print('Partition exists')
    #
    result = my.search_emb_async(embs=embedding, top_k=50)
    print(result)