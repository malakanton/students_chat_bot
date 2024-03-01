import logging
import datetime as dt
from loader import gpt_client
from .prompts import SUMMARY_CONTEXT
from config import MODEL, CHATS_HISTORY


async def gpt_summary(
        chat_id: int
) -> str:
    filepath = CHATS_HISTORY.format(chat_id)
    with open(filepath, 'r') as file:
        message_history = file.read()
    message_history = message_history.replace('<MSG>', '')
    logging.info('start gpt request')
    try:
        today = str(dt.datetime.now().date())
        completion = gpt_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SUMMARY_CONTEXT.format(today)},
                {"role": "user", "content": message_history}
            ]
        )
        summary = completion.choices[0].message.content
        logging.info('finish gpt request')
        return summary
    except:
        logging.error('Didnt receive a reply from OpenAI')
