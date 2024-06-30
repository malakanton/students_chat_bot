import datetime as dt

from loader import gpt_client, cfg
from loguru import logger

from .prompts import SUMMARY_CONTEXT


async def gpt_summary(chat_id: int) -> str:
    filepath = cfg.CHATS_HISTORY.format(chat_id)
    with open(filepath, "r") as file:
        message_history = file.read()
    message_history = message_history.replace("<MSG>", "")
    logger.info("start gpt request")
    try:
        today = str(dt.datetime.now().date())
        completion = gpt_client.chat.completions.create(
            model=cfg.SUMMARY_MODEL,
            messages=[
                {"role": "system", "content": SUMMARY_CONTEXT.format(today)},
                {"role": "user", "content": message_history},
            ],
        )
        summary = completion.choices[0].message.content
        logger.info("finish gpt request")
        return summary
    except Exception as e:
        logger.error(f"Didnt receive a reply from OpenAI, error occured {e}")
