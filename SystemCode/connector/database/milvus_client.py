from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility, \
    Partition
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from functools import partial
import time
import copy
from datetime import datetime
from SystemCode.configs.database import MYSQL_LOCAL_HOST, MYSQL_REMOTE_HOST, MILVUS_PORT, MILVUS_USER, \
    MILVUS_PASSWORD, MILVUS_DB_NAME, CHUNK_SIZE, VECTOR_SEARCH_TOP_K, VECTOR_SEARCH_TOP_K_RERANK
from langchain.docstore.document import Document
import math
import logging
from itertools import groupby
from typing import List
from SystemCode.configs.basic import LOG_LEVEL


# ----------------- Logger -----------------
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', force=True)


class MilvusFailed(Exception):
    """异常基类"""
    pass


class MilvusClient:
    def __init__(self, mode, user_id, kb_ids, *, threshold=0.475, client_timeout=3, gpu_enable=False):
        self.user_id = user_id
        self.kb_ids = kb_ids if isinstance(kb_ids, list) else [kb_ids]

        if mode == 'local':
            self.host = MYSQL_LOCAL_HOST
        else:
            self.host = MYSQL_REMOTE_HOST
        self.port = MILVUS_PORT
        self.user = MILVUS_USER
        self.password = MILVUS_PASSWORD
        self.db_name = MILVUS_DB_NAME
        self.client_timeout = client_timeout
        self.threshold = threshold      # use to filter the search result, default is 0.475, rerank score
        self.sess: Collection = None
        self.partitions: List[Partition] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.top_k = VECTOR_SEARCH_TOP_K
        self.top_k_rerank = VECTOR_SEARCH_TOP_K_RERANK
        self.search_params = {"metric_type": "L2", "params": {"nprobe": 256}}
        if not gpu_enable:
            self.create_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 2048}}
        else:
            self.create_params = {"metric_type": "L2", "index_type": "GPU_IVF_FLAT", "params": {"nlist": 2048}}
        self.last_init_ts = time.time() - 100  # 减去100保证最初的init不会被拒绝
        self.init()

    @property
    def fields(self):
        fields = [
            FieldSchema(name='chunk_id', dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name='file_id', dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name='file_name', dtype=DataType.VARCHAR, max_length=640),
            FieldSchema(name='file_path', dtype=DataType.VARCHAR, max_length=640),
            FieldSchema(name='timestamp', dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name='content', dtype=DataType.VARCHAR, max_length=4000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=768)
        ]
        return fields

    def parse_batch_result(self, batch_result):
        new_result = []
        for batch_idx, result in enumerate(batch_result):
            new_cands = []
            result.sort(key=lambda x: x.score, reverse=True)
            valid_results = [cand for cand in result if cand.score >= self.threshold]
            if len(valid_results) == 0 or len(valid_results) > self.top_k_rerank:  # 如果没有合适的结果或者结果大于topk，就取topk
                valid_results = result[:self.top_k_rerank]

            for cand_i, cand in enumerate(valid_results):
                doc = Document(page_content=cand.entity.get('content'),
                               metadata={"score": cand.score, "file_id": cand.entity.get('file_id'),
                                         "file_name": cand.entity.get('file_name'),
                                         "chunk_id": cand.entity.get('chunk_id')})
                new_cands.append(doc)
            # csv和xlsx文件不做expand_cand_docs
            need_expand, not_need_expand = [], []
            for doc in new_cands:
                if doc.metadata['file_name'].lower().split('.')[-1] in ['csv', 'xlsx']:
                    doc.metadata["kernel"] = doc.page_content
                    not_need_expand.append(doc)
                else:
                    need_expand.append(doc)
            expand_res = self.expand_cand_docs(need_expand)
            new_cands = not_need_expand + expand_res
            new_result.append(new_cands)
        return new_result

    @property
    def output_fields(self):
        return ['chunk_id', 'file_id', 'file_name', 'file_path', 'timestamp', 'content']

    def init(self):
        try:
            connections.connect(host=self.host, port=self.port, user=self.user,
                                password=self.password, db_name=self.db_name)  # timeout=3 [cannot set]
            if utility.has_collection(self.user_id):
                self.sess = Collection(self.user_id)
                logging.info(f'collection {self.user_id} exists')
            else:
                schema = CollectionSchema(self.fields)
                logging.info(f'create collection {self.user_id} {schema}')
                self.sess = Collection(self.user_id, schema)
                self.sess.create_index(field_name="embedding", index_params=self.create_params)
            for kb_id in self.kb_ids:
                if not self.sess.has_partition(kb_id):
                    self.sess.create_partition(kb_id)
            self.partitions = [Partition(self.sess, kb_id) for kb_id in self.kb_ids]
            logging.info('partitions: %s', self.kb_ids)
            self.sess.load()
        except Exception as e:
            logging.error(e)

    def __search_emb_sync(self, embs, expr='', model_manager=None, top_k=None, client_timeout=None, queries=None):

        if not top_k:
            top_k = self.top_k
        milvus_records = self.sess.search(data=embs, partition_names=self.kb_ids, anns_field="embedding",
                                          param=self.search_params, limit=top_k,
                                          output_fields=self.output_fields, expr=expr, timeout=client_timeout)

        # 2nd retrival
        if model_manager and queries:
            # rerank for each query
            for query, record in zip(queries, milvus_records):
                rerank_results = model_manager.rerank(query, [hit.entity.get('content') for hit in record])
                # change distance to score, and update the record
                # due to shared memory, the record will be updated in the milvus_records
                for score, qid in zip(rerank_results['rerank_scores'], rerank_results['rerank_ids']):
                    record[qid].distance = score

        milvus_records_proc = self.parse_batch_result(milvus_records)
        # debug_logger.info(milvus_records)

        return milvus_records_proc

    def search_emb_async(self, embs, expr='', model_manager=None, top_k=None, client_timeout=None,
                         queries=None):
        if not top_k:
            top_k = self.top_k
        # 将search_emb_sync函数放入线程池中运行
        future = self.executor.submit(self.__search_emb_sync, embs, expr, model_manager, top_k, client_timeout,
                                      [queries] if isinstance(queries, str) else queries)
        return future.result()

    def query_expr_async(self, expr, output_fields=None, client_timeout=None):
        if client_timeout is None:
            client_timeout = self.client_timeout
        if not output_fields:
            output_fields = self.output_fields
        future = self.executor.submit(
            partial(self.sess.query, partition_names=self.kb_ids, output_fields=output_fields, expr=expr,
                    timeout=client_timeout))
        return future.result()

    def insert_files_not_async(self, file_id, file_name, file_path, docs, embs, batch_size=1000):
        logging.info(f'[ FILE ]now insert_file {file_name}')
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M")
        # loop = asyncio.get_running_loop()
        contents = [doc.page_content for doc in docs]
        num_docs = len(docs)
        for batch_start in range(0, num_docs, batch_size):
            batch_end = min(batch_start + batch_size, num_docs)
            data = [[] for _ in range(len(self.sess.schema))]

            for idx in range(batch_start, batch_end):
                cont = contents[idx]
                emb = embs[idx]
                chunk_id = f'{file_id}_{idx}'
                data[0].append(chunk_id)
                data[1].append(file_id)
                data[2].append(file_name)
                data[3].append(file_path)
                data[4].append(timestamp)
                data[5].append(cont)
                data[6].append(emb)

            # 执行插入操作
            try:
                logging.info('Inserting into Milvus...')
                mr = self.partitions[0].insert(data=data)
                logging.info(f'{file_name} {mr}')
            except Exception as e:
                logging.error(f'Milvus insert file_id:{file_id}, file_name:{file_name} failed: {e}')
                return False

        return True

    async def insert_files(self, file_id, file_name, file_path, docs, embs, batch_size=1000):
        logging.info(f'[ FILE ]now insert_file {file_name}')
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M")
        loop = asyncio.get_running_loop()
        contents = [doc.page_content for doc in docs]
        num_docs = len(docs)
        for batch_start in range(0, num_docs, batch_size):
            batch_end = min(batch_start + batch_size, num_docs)
            data = [[] for _ in range(len(self.sess.schema))]

            for idx in range(batch_start, batch_end):
                cont = contents[idx]
                emb = embs[idx]
                chunk_id = f'{file_id}_{idx}'
                data[0].append(chunk_id)
                data[1].append(file_id)
                data[2].append(file_name)
                data[3].append(file_path)
                data[4].append(timestamp)
                data[5].append(cont)
                data[6].append(emb)

            # 执行插入操作
            try:
                logging.info('Inserting into Milvus...')
                mr = await loop.run_in_executor(
                    self.executor, partial(self.partitions[0].insert, data=data))
                logging.info(f'{file_name} {mr}')
            except Exception as e:
                logging.error(f'Milvus insert file_id:{file_id}, file_name:{file_name} failed: {e}')
                return False

        return True

    def delete_collection(self):
        self.sess.release()
        utility.drop_collection(self.user_id)

    def delete_partition(self, partition_name):
        part = Partition(self.sess, partition_name)
        part.release()
        self.sess.drop_partition(partition_name)

    def delete_files(self, file_id):
        self.sess.delete(expr=f"file_id in {file_id}")
        logging.info('milvus delete files_id: %s', file_id)

    def get_files(self, files_id):
        res = self.query_expr_async(expr=f"file_id in {files_id}", output_fields=["file_id"])
        valid_ids = [result['file_id'] for result in res]
        return valid_ids

    def seperate_list(self, ls: List[int]) -> List[List[int]]:
        lists = []
        ls1 = [ls[0]]
        for i in range(1, len(ls)):
            if ls[i - 1] + 1 == ls[i]:
                ls1.append(ls[i])
            else:
                lists.append(ls1)
                ls1 = [ls[i]]
        lists.append(ls1)
        return lists

    def process_group(self, group):
        new_cands = []
        # 对每个分组按照chunk_id进行排序
        group.sort(key=lambda x: int(x.metadata['chunk_id'].split('_')[-1]))
        id_set = set()
        file_id = group[0].metadata['file_id']
        file_name = group[0].metadata['file_name']
        group_scores_map = {}
        # 先找出该文件所有需要搜索的chunk_id
        cand_chunks_set = set()  # 使用集合而不是列表
        for cand_doc in group:
            current_chunk_id = int(cand_doc.metadata['chunk_id'].split('_')[-1])
            group_scores_map[current_chunk_id] = cand_doc.metadata['score']
            # 使用 set comprehension 一次性生成区间内所有可能的 chunk_id
            chunk_ids = {file_id + '_' + str(i) for i in range(current_chunk_id - 200, current_chunk_id + 200)}
            # 更新 cand_chunks_set 集合
            cand_chunks_set.update(chunk_ids)

        cand_chunks = list(cand_chunks_set)

        group_relative_chunks = self.query_expr_async(expr=f"file_id == \"{file_id}\" and chunk_id in {cand_chunks}",
                                                      output_fields=["chunk_id", "content"])
        group_chunk_map = {int(item['chunk_id'].split('_')[-1]): item['content'] for item in group_relative_chunks}
        group_file_chunk_num = list(group_chunk_map.keys())
        for cand_doc in group:
            current_chunk_id = int(cand_doc.metadata['chunk_id'].split('_')[-1])
            doc = copy.deepcopy(cand_doc)
            id_set.add(current_chunk_id)
            docs_len = len(doc.page_content)
            for k in range(1, 200):
                break_flag = False
                for expand_index in [current_chunk_id + k, current_chunk_id - k]:
                    if expand_index in group_file_chunk_num:
                        merge_content = group_chunk_map[expand_index]
                        if docs_len + len(merge_content) > CHUNK_SIZE:
                            break_flag = True
                            break
                        else:
                            docs_len += len(merge_content)
                            id_set.add(expand_index)
                if break_flag:
                    break

        id_list = sorted(list(id_set))
        id_lists = self.seperate_list(id_list)
        for id_seq in id_lists:
            try:
                for id in id_seq:
                    if id == id_seq[0]:
                        doc = Document(page_content=group_chunk_map[id],
                                       metadata={"score": 0, "file_id": file_id,
                                                 "file_name": file_name})
                    else:
                        doc.page_content += " " + group_chunk_map[id]
                doc_score = min([group_scores_map[id] for id in id_seq if id in group_scores_map])
                doc.metadata["score"] = float(format(1 - doc_score / math.sqrt(2), '.4f'))
                doc.metadata["kernel"] = '|'.join([group_chunk_map[id] for id in id_seq if id in group_scores_map])
                new_cands.append(doc)
            except Exception as e:
                logging.error(
                    f"process_group error: {e}. maybe chunks in ES not exists in Milvus. Please delete the file and upload again.")
        return new_cands

    def expand_cand_docs(self, cand_docs):
        cand_docs = sorted(cand_docs, key=lambda x: x.metadata['file_id'])
        # 按照file_id进行分组
        m_grouped = [list(group) for key, group in groupby(cand_docs, key=lambda x: x.metadata['file_id'])]
        logging.info('milvus group number: %s', len(m_grouped))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for group in m_grouped:
                if not group:
                    continue
                future = executor.submit(self.process_group, group)
                futures.append(future)

            new_cands = []
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    new_cands.extend(result)
            return new_cands


if __name__ == '__main__':
    test = MilvusClient(
        mode='remote',
        user_id='carey',
        kb_ids=['test'],
        threshold=1.1,
        client_timeout=3,
        gpu_enable=False
    )

    print(1)

    from BCEmbedding import EmbeddingModel
    from SystemCode.core.file import File

    file = File(
        file_id='test',
        file_name='斗破苍穹.txt',
        file_path='../../core/斗破苍穹.txt',
        kb_id='test',
    )

    print(2)
    docs = file.split_file('None')
    print(3)

    embed_model = EmbeddingModel(model_name_or_path='../../server/models/bce-embedding-base_v1')
    embeddings = embed_model.encode([doc.page_content for doc in docs])

    import numpy as np

    # np.save('embeddings.npy', embeddings)
    # embeddings = np.load('embeddings.npy')

    while True:
        time.sleep(1)
