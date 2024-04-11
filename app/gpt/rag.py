from config import BLABLA_MODEL, SUBJ_CLF_TH, INFO_COLLECTION
from loader import gpt_client, vector_db, embeddings, subjects_vector_db
from gpt.vector_db import IntentClassifier
from gpt.prompts import RAG_HELPER, HELPER
from loguru import logger
import datetime as dt


def gpt_respond(query: str, chunks: int = 3, th=SUBJ_CLF_TH) -> str:
    date = dt.datetime.now().date().ctime()
    ic = IntentClassifier(query, th, embeddings, subjects_vector_db)
    subject = ic.subject_clf()
    if subject:
        logger.info(f'subject initialized, subject code: {subject}')
        search_results = vector_db.similarity_search_by_vector(
            ic.vector,
            k=chunks,
            filter={"source": INFO_COLLECTION, 'subject': subject}
        )
        logger.info(f'Similarity search results: {str(search_results)}')
        rag_text = '\n'.join([doc.page_content for doc in search_results])
        messages = [
            {"role": "system", "content": RAG_HELPER.format(date)},
            {"role": "system", "content": rag_text},
            {"role": "user", "content": query}
        ]
        temp = 0.5
    else:
        messages = [
            {"role": "system", "content": HELPER.format(date)},
            {"role": "user", "content": query}
        ]
        temp = 0.8
    completion = gpt_client.chat.completions.create(
        model=BLABLA_MODEL,
        messages=messages,
        temperature=temp,
        max_tokens=4096
    )
    respond = completion.choices[0].message.content
    return respond


