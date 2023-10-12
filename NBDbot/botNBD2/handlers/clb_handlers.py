from aiogram import Router, Bot
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, URLInputFile
from apiNBD import API
import json

from botNBD.custom_keyboards import reply_keys, inline_keys
from botNBD.my_filters import filters
clbs = Router()
bot2 = Bot(token=API.get_token())


async def get_sug(clb: CallbackQuery, orient: str):
    if orient == 'prev':
        sug_info = (await API.Get('pref_suggestion', params={'tg_id': clb.from_user.id})).json()
        sug=sug_info.get('sug')
    elif orient == 'next':
        sug_info = (await API.Get('next_suggestion', params={'tg_id': clb.from_user.id})).json()
        sug=sug_info.get('sug')

    text = f"{sug.get('description')}\n\n{sug.get('price')}\n\nПредложение: {str(sug_info.get('index'))} из {sug_info.get('len')}"
    media = [InputMediaPhoto(media=URLInputFile(sug.get('cover')), caption=sug.get('title'))]

    for item in sug.get('images'):
        media.append(InputMediaPhoto(media=URLInputFile(item)))
    msgs = await bot2.send_media_group(clb.from_user.id, media=media)

    await clb.message.answer(text=text, reply_markup=inline_keys.get_inl_key_sug(
        title_id=msgs,
        btn={
            '<--': 'prev',
            'Ссылка': f'{sug.get("contact")}',
            "-->": "next",
            'Поменять ответы':'pool'}))


@clbs.callback_query(inline_keys.sug_callback.filter())
async def sug_nav(clb: CallbackQuery, callback_data: inline_keys.sug_callback):
    await clb.answer()
    print(callback_data.list_id)
    id_list=callback_data.list_id.split('_')
    unpack_id=[]
    for el in id_list:
        unpack_id.append(int(float(el)*200))
    for el in unpack_id:
        await bot2.delete_message(clb.from_user.id,el)
    await clb.message.delete()
    ms = await clb.message.answer("Загрузка...", reply_keys=inline_keys.get_inl_key(['сброс']))
    await get_sug(clb, callback_data.orient)
    await bot2.delete_message(clb.from_user.id, ms.message_id)


@clbs.callback_query(Text(startswith='linksug'))
async def sug_link(clb: CallbackQuery):
    await clb.answer()
    print(clb.data)

@clbs.callback_query(Text(startswith='pool'))
async def new_pool(clb: CallbackQuery):
    await start_poll(clb)

@clbs.callback_query(filters.StateFilter('after_start'))
async def start_meet(clb: CallbackQuery):
    await clb.message.edit_reply_markup(reply_markup=None)
    await API.Post('set_user_state', data={'id': clb.from_user.id, 'state': 'meet'})
    question = (await API.Get('get_meet_question', params={'tg_id': clb.from_user.id})).json()
    await clb.message.answer(text=question.get('question'),
                             reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
    await clb.answer()

@clbs.callback_query(filters.StateFilter('after_meet'))
async def start_poll(clb: CallbackQuery):
    await clb.answer()
    await clb.message.edit_reply_markup(reply_markup=None)
    await API.Post('set_user_state', data={'id': clb.from_user.id, 'state': 'poll_main'})
    question = (await API.Get('get_main_question', params={'tg_id': clb.from_user.id})).json()
    await clb.message.answer(text=question.get('question'),
                             reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))



