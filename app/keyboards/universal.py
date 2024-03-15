from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.buttons import NewsLetter
from keyboards.callbacks import ConfirmCallback


async def send_newsletter_kb():
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=button.value,
            callback_data=ConfirmCallback(
                cnf=button.name
            ).pack()
        )
        for button in NewsLetter]
    kb_builder.row(*(buttons), width=2)
    return kb_builder.as_markup()
