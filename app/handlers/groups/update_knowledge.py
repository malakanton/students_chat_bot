from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from gpt.vector_db import DocumentsHandler
from handlers.routers import groups_router
from langchain_community.document_loaders import TextLoader
from lib.misc import prep_markdown
from loader import bot, conn_str, embeddings, gd, vector_db, lx
from lib.config.config import cfg
from loguru import logger


@groups_router.message(
    Command("knowledge_update"), F.chat.id == int(cfg.secrets.ADMIN_CHAT)
)
async def update_knowlage(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_document")
    if update_collection(cfg.INFO_COLLECTION):
        await message.answer(prep_markdown(lx.COLLECTION_UPDATED))
    else:
        await message.answer(prep_markdown(lx.COLLECTION_NOT_UPDATED))
    await message.delete()


@groups_router.message(
    Command("subjects_update"), F.chat.id == int(cfg.secrets.ADMIN_CHAT)
)
async def update_subjects_triggers(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_document")
    if update_collection(cfg.SUBJECTS_COLLECTION):
        await message.answer(prep_markdown(lx.SUBJECTS_UPDATED))
    else:
        await message.answer(prep_markdown(lx.COLLECTION_NOT_UPDATED))
    await message.delete()


def update_collection(collection: str) -> bool:
    logger.info("Start vector collection updating")
    file_name = collection + ".txt"
    file_path = gd.download_file(file_name)
    if not file_path:
        logger.info(f"failed to download file {file_name}")
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
