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
from config import SUBJECTS_COLLECTION, INFO_COLLECTION, ADMIN_CHAT


@groups_router.message(
            Command('knowledge_update'),
            F.chat.id == int(ADMIN_CHAT)
            )
async def update_knowlage(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_document")
    if update_collection(INFO_COLLECTION):
        await message.answer(prep_markdown(lx.COLLECTION_UPDATED))
    else:
        await message.answer(prep_markdown(lx.COLLECTION_NOT_UPDATED))
    await message.delete()


@groups_router.message(
            Command('subjects_update'),
            F.chat.id == int(ADMIN_CHAT)
            )
async def update_subjects_triggers(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_document")
    if update_collection(SUBJECTS_COLLECTION):
        await message.answer(prep_markdown(lx.SUBJECTS_UPDATED))
    else:
        await message.answer(prep_markdown(lx.COLLECTION_NOT_UPDATED))
    await message.delete()


def update_collection(collection: str) -> bool:
    logger.info('Start vector collection updating')
    file_name = collection + '.txt'
    file_path = gd.download_file(file_name)
    if not file_path:
        logger.info(f'failed to download file {file_name}')
        return False
    docs = TextLoader(file_path).load()
    dh = DocumentsHandler(docs)
    vector_db.from_documents(
        embedding=embeddings,
        documents=dh.prep_subjects_infos(collection),
        collection_name=collection,
        connection_string=conn_str,
        pre_delete_collection=True,
    )
    return True
