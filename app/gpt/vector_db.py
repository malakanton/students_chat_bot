import re
from typing import List

from config import INFO_COLLECTION, SUBJECTS_COLLECTION
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings
from loguru import logger

text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=32)


class DocumentsHandler:
    raw_documents: List[Document]
    subj_pattern: re.Pattern
    text_splitter: RecursiveCharacterTextSplitter

    def __init__(self, raw_documents: List[Document]):
        self.raw_documents = raw_documents[0].page_content
        self.subj_pattert = re.compile(r"<[a-z_]*>")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=256, chunk_overlap=32
        )
        self._collection_dict = {
            SUBJECTS_COLLECTION: "subjects",
            INFO_COLLECTION: "subjects_info",
        }

    def _split_documents(self) -> List[str]:
        return [text.strip() for text in self.raw_documents.split("<subj>") if text]

    def prep_subjects_tags(self, source: str) -> List[Document]:
        documents, metadatas = [], []
        texts = self._split_documents()
        for i, doc in enumerate(texts):
            subj = re.search(self.subj_pattert, doc).group(0)
            doc = re.sub(self.subj_pattert, "", doc).strip()
            meta = {"source": source, "id": str(i), "subject": subj}
            documents.append(doc)
            metadatas.append(meta)
        return self.text_splitter.create_documents(documents, metadatas=metadatas)

    def prep_subjects_infos(self, collection: str) -> List[Document]:
        documents_prepped = self.prep_subjects_tags(
            source=self._collection_dict.get(collection, collection)
        )
        return self.text_splitter.split_documents(documents_prepped)


class IntentClassifier:
    query: str
    vector: list[float]
    th: float
    embeddings: OpenAIEmbeddings
    vector_db: PGVector

    def __init__(
        self, query: str, th: float, embeddings: OpenAIEmbeddings, vector_db: PGVector
    ) -> None:
        self.query = query
        self.th = th
        self.embeddings = embeddings
        self.vector_db = vector_db
        self.vector = self._vectorize(query)

    def _vectorize(self, query: str) -> list[float]:
        return self.embeddings.embed_query(query)

    def subject_clf(self) -> str | None:
        res = self.vector_db.similarity_search_with_score_by_vector(self.vector, k=1)
        print(res)
        try:
            doc, score = res[0][0], res[0][1]
            logger.info(f"Similarity score for query is {score}")
            if score <= self.th:
                return doc.metadata["subject"]
            else:
                return None
        except IndexError:
            return None
