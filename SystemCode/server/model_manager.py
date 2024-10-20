import logging
import numpy as np
from BCEmbedding import EmbeddingModel, RerankerModel
from SystemCode.connector.database.milvus_client import MilvusClient
from SystemCode.configs.database import CONNECT_MODE


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)


class ModelManager:
    def __init__(self):
        logging.info("[ModelManager]Loading embedding model and reranker model...")
        self.embedding_model = EmbeddingModel(model_name_or_path="maidalun1020/bce-embedding-base_v1")
        logging.info("[ModelManager]Embedding model loaded.")
        self.reranker_model = RerankerModel(model_name_or_path="maidalun1020/bce-reranker-base_v1")
        logging.info("[ModelManager]Reranker model loaded.")

    def get_embedding(self, docs) -> np.array:
        docs_content = [doc.page_content for doc in docs]

        return self.embedding_model.encode(docs_content)

    def rerank(self, query, passages):
        sentence_pairs = [[query, passage] for passage in passages]
        # scores = self.reranker_model.compute_score(sentence_pairs)
        rerank_results = self.reranker_model.rerank(query, passages)

        return rerank_results

    def retrieval(self, user_id, kb_ids, query):
        q_embedding = self.embedding_model.encode([query])

        milvus_client = MilvusClient(
            user_id=user_id,
            kb_ids=kb_ids,
            mode=CONNECT_MODE
        )

        retrieval_docs = milvus_client.search_emb_async(
            embs=q_embedding,
            model_manager=self,
            top_k=100,
            queries=[query]
        )

        return retrieval_docs


if __name__ == '__main__':



    class Doc:
        def __init__(self, page_content):
            self.page_content = page_content

    model_manager = ModelManager()
    docs = model_manager.retrieval(
        user_id='U3e6e0a3b608648e39cf8f9c37ec57c8f',
        kb_ids=['KB67225a562f6c4594914b76c20388c477'],
        query="什么是machine learning"
    )

    print(model_manager.get_embedding([Doc("hello world")]))
    print(model_manager.rerank("hello", ["hello world", "bird"]))