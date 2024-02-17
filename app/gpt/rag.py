from langchain_community.document_loaders import TextLoader
from langchain.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
from config import OPEN_AI_URL, OPEN_AI_API_KEY, PG_PASS
from loader import gpt_client
from .prompts import RAG_HELPER
import logging


CONN_STRING = f'postgresql+psycopg2://postgres:{PG_PASS}@51.250.109.13:5433/vector_db'
COLLECTION = 'test_collection'



embeddings = OpenAIEmbeddings(
    base_url=OPEN_AI_URL,
    api_key=OPEN_AI_API_KEY
)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512, chunk_overlap=32
)

vector_db = PGVector.from_existing_index(
    embedding=embeddings,
    collection_name=COLLECTION,
    connection_string=CONN_STRING,
)


def gpt_respond(query: str, chunks: int = 3) -> str:
    search_results = vector_db.similarity_search_with_score(query, k=chunks)
    rag_text = '\n'.join([doc[0].page_content for doc in search_results])
    logging.debug('rag_text')
    completion = gpt_client.chat.completions.create(
      model="gpt-3.5-turbo-1106",
      messages=[
          {"role": "system", "content": RAG_HELPER},
          {"role": "system", "content": rag_text},
          {"role": "user", "content": query}
      ],
        temperature=0.5,
        max_tokens=4096
    )
    respond = completion.choices[0].message.content
    return respond
