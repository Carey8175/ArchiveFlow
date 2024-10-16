import logging
import numpy as np
from BCEmbedding import EmbeddingModel, RerankerModel


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
