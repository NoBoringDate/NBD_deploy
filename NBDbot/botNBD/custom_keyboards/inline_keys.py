from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from apiNBD import API


def get_inl_key(btn: list, adj=2):
    builder = InlineKeyboardBuilder()
    for el in btn:
        builder.add(InlineKeyboardButton(text=el, callback_data=el))
    builder.adjust(adj)
    return builder.as_markup()


def get_inl_key_start(btn:dict, adj=2):
    builder = InlineKeyboardBuilder()
    for el in btn:
        builder.add(InlineKeyboardButton(text=el, callback_data=btn.get(el)))
    builder.adjust(adj)
    return builder.as_markup()

def get_inl_key_get(btn: str, adj=2):
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text=btn, callback_data='start_sug_view'))
    builder.adjust(adj)
    return builder.as_markup()

class sug_callback(CallbackData, prefix="m"):
    list_id: str
    orient: str


async def get_inl_key_sug(btn: dict,key, adj=0):
    builder = InlineKeyboardBuilder()

    key=key
    for el in btn:
        if el == "Связаться":
            if (((btn.get(el))[1:2]).strip()).isdigit():
                builder.add(InlineKeyboardButton(text=el, callback_data="tel:"+btn.get(el).strip()))
            else:
                builder.add(InlineKeyboardButton(text=el, url=btn.get(el).strip()))
        elif btn.get(el) =='pool':
            builder.add(InlineKeyboardButton(text=el, callback_data=sug_callback(orient='new', list_id=key.get('name')).pack()))
        elif el == 'Подробнее':
            builder.add(InlineKeyboardButton(text=el, callback_data=sug_callback(orient=btn.get(el), list_id=key.get('name')).pack()))
        else:
            stroka=key.get('name')
            ori=btn.get(el)
            data=sug_callback(orient=ori, list_id=stroka).pack()
            builder.add(InlineKeyboardButton(text=el, callback_data=data))
    if adj == 0:
        builder.adjust(3,1,1)
    else:
        builder.adjust(*adj)
    return builder.as_markup()
