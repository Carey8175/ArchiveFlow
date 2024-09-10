from typing import List, Union, Callable
from SystemCode.configs.basic import SENTENCE_SIZE
from SystemCode.utils.chinese_text_splitter import ChineseTextSplitter
from SystemCode.utils.loader import UnstructuredPaddleImageLoader, UnstructuredPaddlePDFLoader
from langchain_community.document_loaders import UnstructuredFileLoader, TextLoader, UnstructuredWordDocumentLoader


class File:
    def __init__(self, file_id, kb_id, file_name, file_path):
        self.file_id = file_id
        self.kb_id = kb_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_url = ''
        self._init_type()

    def __str__(self):
        return f"File(file_id={self.file_id}, kb_id={self.kb_id}, file_name={self.file_name}, file_path={self.file_path}, status={self.status}, timestamp={self.timestamp}, deleted={self.deleted}, file_size={self.file_size}, content_length={self.content_length}, chunk_size={self.chunk_size})"

    def __repr__(self):
        return self.__str__()

    def _init_type(self):
        if self.file_path.lower().endswith(".md"):
            self.type = "md"
        elif self.file_path.lower().endswith(".txt"):
            self.type = "txt"
        elif self.file_path.lower().endswith(".pdf"):
            self.type = "pdf"
        elif self.file_path.lower().endswith(".jpg") or self.file_path.lower().endswith(".png") or self.file_path.lower().endswith(".jpeg"):
            self.type = "img"
        elif self.file_path.lower().endswith(".docx"):
            self.type = "docx"
        elif isinstance(file, str):
            self.file_location = "URL"
            self.file_content = b''
            self.file_url = file
        else:
            self.type = None

    def to_dict(self):
        return {
            "file_id": self.file_id,
            "kb_id": self.kb_id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "type": self.type
        }

    def split_file(self, ocr_engine: Callable, sentence_size=SENTENCE_SIZE):
        if self.type == "md":
            loader = UnstructuredFileLoader(self.file_path, mode="elements")
            docs = loader.load()
        elif self.type == "txt":
            loader = TextLoader(self.file_path, autodetect_encoding=True)
            texts_splitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
            docs = loader.load_and_split(texts_splitter)
        elif self.type == "pdf":
            loader = UnstructuredPaddlePDFLoader(self.file_path, ocr_engine)
            texts_splitter = ChineseTextSplitter(pdf=True, sentence_size=sentence_size)
            docs = loader.load_and_split(texts_splitter)
        elif self.type == "img":
            loader = UnstructuredPaddleImageLoader(self.file_path, ocr_engine, mode="elements")
            txt_file_path = loader.turn_to_txt_file()
            loader = TextLoader(txt_file_path, autodetect_encoding=True)
            texts_splitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
            docs = loader.load_and_split(texts_splitter)
        elif self.type == "docx":
            loader = UnstructuredWordDocumentLoader(self.file_path, mode="elements")
            docs = loader.load()
        else:
            docs = []

        return docs


if __name__ == '__main__':
    import uuid
    from paddleocr import PaddleOCR

    ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, show_log=True)
    file = File(uuid.uuid4().hex, uuid.uuid4().hex, "test.png", "test.png")
    docs = file.split_file(ocr_engine)
    1