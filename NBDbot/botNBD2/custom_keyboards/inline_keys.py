from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_inl_key(btn: list, adj=2):
    builder = InlineKeyboardBuilder()
    for el in btn:
        builder.add(InlineKeyboardButton(text=el, callback_data=el))
    builder.adjust(adj)
    return builder.as_markup()


class sug_callback(CallbackData, prefix="m"):
    list_id: str
    orient: str


def get_inl_key_sug(btn: dict, title_id: list, adj=3):
    builder = InlineKeyboardBuilder()
    for el in btn:
        if el == "Ссылка":
            builder.add(InlineKeyboardButton(text=el, url=btn.get(el).strip()))
        elif btn.get(el) =='pool':
            builder.add(InlineKeyboardButton(text=el, callback_data=btn.get(el)))
        else:
            num_list=[]
            id_list = ''
            for msg in title_id:
                print(msg.message_id)
                num_list.append(msg.message_id/200)

            print("##################)")

            for msg in num_list:
                id_list=id_list+ '_'+str(msg)
            stroka=id_list[1:]
            ori=btn.get(el)
            data=sug_callback(orient=ori, list_id=stroka).pack()
            builder.add(InlineKeyboardButton(text=el, callback_data=data))
    builder.adjust(adj)
    return builder.as_markup()
