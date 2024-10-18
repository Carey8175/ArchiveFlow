from pymilvus import Collection
from pymilvus import connections

# 连接到 Milvus 数据库
connections.connect("default", host='47.108.135.173', port='19530')

# 替换为你的集合名
collection_name = 'U3e6e0a3b608648e39cf8f9c37ec57c8f'
collection = Collection(collection_name)
res = collection.query(expr="file_id != ''")
print(res)

file_id = ['F5371478ee02e463fad7b2d355aca7612']

results = collection.query(expr=f"file_id in {file_id}")

if results:
    for result in results:
        print(result)
else:
    print("No result found!")


# collection.delete(expr=f"file_id in {file_id}")

results = collection.query(expr=f"file_id in {file_id}")

# 打印结果
if results:
    for result in results:
        print(result)
else:
    print("No result found!")
