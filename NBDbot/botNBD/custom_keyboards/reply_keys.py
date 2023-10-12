from aiogram.types import KeyboardButton, reply_keyboard_remove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_repl_key(btn: list, adj=2):
    if btn==None:
        return None
    builder = ReplyKeyboardBuilder()
    for el in btn:
        builder.add(KeyboardButton(text=el))
    builder.adjust(adj)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
