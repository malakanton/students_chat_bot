from langchain.vectorstores.pgvector import PGVector
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import OPEN_AI_URL, OPEN_AI_API_KEY, PG_PASS, BLABLA_MODEL
from loader import gpt_client
from .prompts import RAG_HELPER
from loguru import logger

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
    vec = vectorize(query)
    subject = subject_classification(vec)
    search_results = vector_db.similarity_search_with_score(
        query,
        k=chunks,
        filter={"source": "subj_info", 'subject': subject})
    print(search_results)
    rag_text = '\n'.join([doc[0].page_content for doc in search_results])
    logger.debug('rag_text')
    completion = gpt_client.chat.completions.create(
      model=BLABLA_MODEL,
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


def vectorize(query: str) -> list[float]:
    return embeddings.embed_query(query)


def subject_classification(vector: list[float]) -> str:
    res = vector_db.similarity_search_by_vector(vector, k=1)
    if res:
        return res[0].metadata['subject']
    return res