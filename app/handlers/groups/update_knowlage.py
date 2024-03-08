from aiogram import F
from loguru import logger
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from langchain_community.document_loaders import TextLoader

import lib.lexicon as lx
from lib.misc import prep_markdown
from handlers.routers import groups_router
from loader import vector_db, gd, embeddings, conn_str, bot
from gpt.vector_db import DocumentsHandler
from config import CONN_STRING, INFO_COLLECTION, ADMIN_CHAT


@groups_router.message(
            Command('knowledge_update'),
            F.chat.id == int(ADMIN_CHAT)
            )
async def update_knowlage(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_document")
    if update_collection():
        await message.answer(prep_markdown(lx.COLLECTION_UPDATED))
    else:
        await message.answer(prep_markdown(lx.COLLECTION_NOT_UPDATED))
    await message.delete()


def update_collection() -> bool:
    logger.info('Start vector collection updating')
    file_path = gd.download_file('subjects_info.txt')
    if not file_path:
        logger.info('failed to download file subjects_info.txt')
        return False
    docs = TextLoader(file_path).load()
    dh = DocumentsHandler(docs)
    vector_db.from_documents(
        embedding=embeddings,
        documents=dh.prep_subjects_infos(),
        collection_name=INFO_COLLECTION,
        connection_string=conn_str,
        pre_delete_collection=True,
    )
    return True
