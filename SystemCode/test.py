from SystemCode.connector.database.milvus_client import MilvusClient
from SystemCode.server.model_manager import ModelManager
from pymilvus import Collection, utility
import pymilvus

pymilvus.connections.connect(
    host='47.108.135.173',
    port='19530'
)

print(utility.list_collections())
collection = Collection(name='c89149173e4b435cbf0f5be4302086c4')
print(collection.partitions)
p = pymilvus.Partition(collection, 'KB2c83eb356644492cbadd36a176e8b7f3')
print(p.num_entities)


class Doc:
    def __init__(self, page_content):
        self.page_content = page_content


model_manager = ModelManager()
query = ['CNN+LSTM', '什么是ISS？']
emb = model_manager.get_embedding([Doc(query)])


client = MilvusClient(mode='remote', user_id='c89149173e4b435cbf0f5be4302086c4',
                      kb_ids='KB2c83eb356644492cbadd36a176e8b7f3')

for p in client.partitions:
    print(p.num_entities)


result = client.search_emb_async(
    embs=emb,
    model_manager=model_manager,
    top_k=70,
    queries=query
)

1
