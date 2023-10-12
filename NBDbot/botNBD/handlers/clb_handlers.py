from asyncio import sleep
import logging

from aiogram import Router, Bot
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, URLInputFile, ReplyKeyboardRemove
from aiogram.methods import EditMessageReplyMarkup, EditMessageMedia
from apiNBD import API
import json
from botNBD.custom_keyboards import reply_keys, inline_keys
from botNBD.my_filters import filters
clbs = Router()
bot2 = Bot(token=API.get_token())


async def del_img_group(clb: CallbackQuery, callback_data: inline_keys.sug_callback):
    await clb.message.edit_reply_markup(reply_markup=None)
    ids_photo=(await API.Get('get_photo_id', params={'name': callback_data.list_id})).json()

    for el in ids_photo.get('id'):
        try:
            await bot2.delete_message(clb.from_user.id,el)
        except:
            pass
    
    ms = await clb.message.answer("Загрузка...", reply_keys=inline_keys.get_inl_key(['сброс']))
    return ms


async def get_sug(clb: CallbackQuery, orient: str):
    if orient == 'prev':
        sug_info = (await API.Get('pref_suggestion', params={'tg_id': clb.from_user.id})).json()
        sug=sug_info.get('sug')
    elif orient == 'next':
        sug_info = (await API.Get('next_suggestion', params={'tg_id': clb.from_user.id})).json()
        sug=sug_info.get('sug')

    text = f"🎯{sug.get('short_desc')}\n\nПредложение: {str(sug_info.get('index'))} из {sug_info.get('len')}"
    media = [InputMediaPhoto(media=URLInputFile(sug.get('cover')), caption=f"<b>{sug.get('title')}</b>", parse_mode="HTML")]

    for item in sug.get('images'):
        media.append(InputMediaPhoto(media=URLInputFile(item)))
    await sleep(1)
    while True:
        try:
            msgs = await bot2.send_media_group(clb.from_user.id, media=media, request_timeout=60)
            break
        except Exception as ex:
            logging.info(f"proval imgs:\n  {ex}", stack_info=True)
            
    await sleep(1)
    num_list=[]
    for msg_id in msgs:

        num_list.append(msg_id.message_id)
    key=(await API.Post('get_photo_name', data={'photo_id': num_list})).json()
    while True:
        try:
            await clb.message.answer(text=text,
                                     parse_mode="HTML",
                                     reply_markup=await inline_keys.get_inl_key_sug(
                                         key=key,
                                         btn={
                                             '⬅️⬅️': 'prev',
                                             'Подробнее': 'full',
                                             "➡️➡️": "next",
                                             'Связаться': f'{sug.get("contact")}',
                                             'Поменять ответы': 'pool'}))
            break
        except Exception as ex:
            logging.info(f"proval text:\n  {ex}", stack_info=True)


async def get_start_sug(clb: CallbackQuery, sug_info: dict):
    sug = sug_info.get('sug')
    text = f"🎯{sug.get('short_desc')}\n\nПредложение: {str(sug_info.get('index'))} из {sug_info.get('len')}"
    media = [InputMediaPhoto(media=URLInputFile(sug.get('cover')), caption=f"<b>{sug.get('title')}</b>", parse_mode="HTML")]

    for item in sug.get('images'):
        media.append(InputMediaPhoto(media=URLInputFile(item)))
    await sleep(1)
    while True:
        try:
            msgs = await bot2.send_media_group(clb.from_user.id, media=media, request_timeout=60)
            break
        except Exception as ex:
            logging.info(f"proval imgs:\n  {ex}", stack_info=True)
    await sleep(1)
    num_list=[]
    for msg_id in msgs:
        num_list.append(msg_id.message_id)
    key=(await API.Post('get_photo_name', data={'photo_id': num_list})).json()
    while True:
        try:
            await bot2.send_message(chat_id=clb.from_user.id,
                                    text=text,
                                    reply_markup=await inline_keys.get_inl_key_sug(
                                        key=key,
                                        btn={
                                            '⬅️⬅️': 'prev',
                                            'Подробнее' : 'full',
                                            "➡️➡️": "next",
                                            'Связаться': f'{sug.get("contact")}',
                                            'Поменять ответы': 'pool'}))
            break
        except Exception as ex: 
            logging.info(f"proval text:\n  {ex}", stack_info=True)


async def start_sug(clb: CallbackQuery):
    sug_info = (await API.Get('gen_suggestion', params={'tg_id': clb.from_user.id})).json()
    await get_start_sug(clb, sug_info)


@clbs.callback_query(Text(startswith="start_sug_view"))
async def start_sug_clb(clb: CallbackQuery):
    await clb.answer()
    await clb.message.edit_reply_markup(reply_markup=None)
    await start_sug(clb)


@clbs.callback_query(Text(startswith="tel:"))
async def start_sug_clb_tel(clb: CallbackQuery):
    await clb.answer()
    await clb.message.answer(text=clb.data[4:]+"\n\nПожалуйста сообщите, что нашли данное предложение через сервис Нескучное Свидание!\nСпасибо 😊")
    await API.Post("showed_phone_number", data={"tg_id":clb.from_user.id})


@clbs.callback_query(inline_keys.sug_callback.filter())
async def sug_nav(clb: CallbackQuery, callback_data: inline_keys.sug_callback):
    if callback_data.orient == "new":
        ms = await del_img_group(clb, callback_data)
        await start_poll(clb)
        try:
            await clb.message.delete()
        except:
            pass
        try:
            await bot2.delete_message(clb.from_user.id, ms.message_id)
        except:
            pass
    elif callback_data.orient == "full":
        sug_info = (await API.Get('get_suggestion', params={'tg_id': clb.from_user.id})).json()
        sug = sug_info.get('sug')
        text = ""
        if sug.get('address') != None:
            text = f"🎯{sug.get('description')}\n\n💵{sug.get('price')}\n\n📍{sug.get('address')}\n\nПредложение: {str(sug_info.get('index'))} из {sug_info.get('len')}"
        else:
            text = f"🎯{sug.get('description')}\n\n💵{sug.get('price')}\n\nПредложение: {str(sug_info.get('index'))} из {sug_info.get('len')}"
        key = {'name':callback_data.list_id}
        await clb.message.edit_text(text=text,parse_mode="HTML",reply_markup=await inline_keys.get_inl_key_sug(
                                        key=key,
                                        adj=(2,1,1),
                                        btn={
                                            '⬅️⬅️': 'prev',
                                            "➡️➡️": "next",
                                            'Связаться': f'{sug.get("contact")}',
                                            'Поменять ответы': 'pool'}))
    else:
        ms = await del_img_group(clb, callback_data)
        await clb.answer()
        try:
            await clb.message.delete()
        except:
            pass
        await get_sug(clb, callback_data.orient)
        try:
            await bot2.delete_message(clb.from_user.id, ms.message_id)
        except:
            pass


@clbs.callback_query(Text(startswith='linksug'))
async def sug_link(clb: CallbackQuery):
    await clb.answer()
    print(clb.data)


@clbs.callback_query(filters.StateFilterClb('after_start'))
async def start_meet(clb: CallbackQuery):
    if clb.data == "start_meet":
        await clb.message.edit_reply_markup(reply_markup=None)
        await API.Post('set_user_state', data={'id': clb.from_user.id, 'state': 'meet'})
        question = (await API.Get('get_meet_question', params={'tg_id': clb.from_user.id})).json()
        await clb.message.answer(text=question.get('question'),
                                reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
        await clb.answer()
    elif clb.data == "start_poll":
        await clb.message.edit_reply_markup(reply_markup=None)
        text = (await API.Get('get_text', params={'func': 'meet_end', 'variable': 2})).json()
        start_btn = (await API.Get('get_text', params={'func': 'pool_start', 'variable': 2})).json()
        await API.Post('set_user_state', data={'id': clb.from_user.id, 'state': 'after_meet'})
        await clb.message.answer(text=text.get('text'), reply_markup=inline_keys.get_inl_key([start_btn.get('text')]))
    elif clb.data == "start_poll2":
        await clb.message.edit_reply_markup(reply_markup=None)
        text = (await API.Get('get_text', params={'func': 'meet_end', 'variable': 3})).json()
        start_btn = (await API.Get('get_text', params={'func': 'pool_start', 'variable': 3})).json()
        await API.Post('set_user_state', data={'id': clb.from_user.id, 'state': 'after_meet'})
        await clb.message.answer(text=text.get('text'), reply_markup=inline_keys.get_inl_key([start_btn.get('text')]))


@clbs.callback_query(filters.StateFilterClb('after_meet'))
async def start_poll(clb: CallbackQuery):
    await clb.answer()
    try:
        await clb.message.edit_reply_markup(reply_markup=None)
    except:
        pass
    await API.Post('set_user_state', data={'id': clb.from_user.id, 'state': 'poll_main'})
    question = (await API.Get('get_main_question', params={'tg_id': clb.from_user.id, 'new':False})).json()
    await clb.message.answer(text=question.get('question'),
                             reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
"""     try:
        await clb.message.delete()
    except:
        pass """


@clbs.callback_query(Text(startswith="new"))
async def clb_start_poll(clb: CallbackQuery):
    await start_poll(clb)


@clbs.callback_query(Text(startswith="allsend:"))
async def start_sug_clb_send(clb: CallbackQuery):
    await API.Get('global_statistic', params={"send_message":clb.message.text, "tg_id":clb.from_user.id, "button_id":clb.data[8:]})
    await start_poll(clb)


@clbs.callback_query(Text(startswith="advertsend:"))
async def start_sug_clb_group(clb: CallbackQuery):
    key_from_clb = clb.data.split(":")
    await clb.message.edit_reply_markup(reply_markup=None)
    await API.Get('global_statistic', params={"send_message":clb.message.text, "tg_id":clb.from_user.id, "button_id":key_from_clb[1]})
    sug_info = (await API.Get('start_advert_sug', params={"tg_id":clb.from_user.id, "key_button":key_from_clb[1]})).json()
    if key_from_clb[1] == "23.02.1":
        await clb.message.answer(text="Правильный выбор! Держи мою подборку!")
        await get_start_sug(clb, sug_info)
    elif key_from_clb[1] == "23.02.2":
        await clb.message.answer(text="Интересно, что бы это могло быть 🧐 А вот моя подборка то, что можно подарить!")
        await get_start_sug(clb, sug_info)
    else:
        await clb.message.answer(text="Интересно, я запишу👌\nА теперь держи мою подборку!")
        await get_start_sug(clb, sug_info)


@clbs.callback_query(Text(startswith="lottery:"))
async def clb_lottery(clb: CallbackQuery):
    key_from_clb = clb.data.split(":")
    await API.Get('global_statistic', params={"send_message":clb.message.text, "tg_id":clb.from_user.id, "button_id":key_from_clb[1]})
    if key_from_clb[1] == "go":
        link = (await API.Get('lottery', params={"tg_id":clb.from_user.id})).json()
        if link["ref_link"]:
            await clb.answer()
            await clb.message.answer(text="Удачи!\nВот твоя ссылка для приглашения друзей (ее так же можно получить через меню):")
            await clb.message.answer(text=link["ref_link"],reply_markup=inline_keys.get_inl_key_start(btn={"Подобрать место для встречи":"new"}))
        else:
            await clb.answer(text="Ты уже участвуешь")
    elif key_from_clb[1] == "nope":
        await clb.answer()
        await clb.message.answer(text="Зря ты, конечно, отказываешься! Однако можешь посмотреть актуальные подборки, вдруг приглянется что-нибудь! 😉",
                           reply_markup=inline_keys.get_inl_key_start(btn={"Подобрать место для встречи":"new"}))
