import random

from aiogram import Router, Bot
from aiogram.types import Message, InputMediaPhoto, URLInputFile, ReplyKeyboardRemove
from apiNBD import API
from botNBD.custom_keyboards import reply_keys, inline_keys
from botNBD.my_filters import filters
from botNBD.handlers.clb_handlers import start_sug
import json
msgs = Router()


@msgs.message(filters.StateFilterMsg('bug'))
async def echo_handler(msg: Message) -> None:
    await API.Get('bug_report', params={'tg_id': msg.from_user.id, "bug_report": msg.text})
    text = (await API.Get('get_text', params={'func': 'bug', 'variable': 2})).json()
    await msg.answer((text.get('text')).format(msg.from_user.first_name))
    await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'free'})


@msgs.message(filters.StateFilterMsg('meet'))
async def meet_answer(msg: Message):
    tag = (await API.Get('get_tag', params={'tg_id': msg.from_user.id})).json()
    answer = (await API.Post('meet_answer', data={'id': msg.from_user.id, tag.get('tag'): msg.text})).json()
    if answer.get('error'):
        await msg.answer(text=((await API.Get('get_text', params={'func': 'age_valid_erorr', 'variable': 1})).json()).get('text'))
        question = answer.get('question')
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))

        return None
    text = random.choice(answer.get('answer_to_answer'))
    question = (await API.Get('get_meet_question', params={'tg_id': msg.from_user.id})).json()
    if question.get('session'):
        await msg.answer(text=text, reply_markup=reply_keys.reply_keyboard_remove)
        text = (await API.Get('get_text', params={'func': 'meet_end', 'variable': 1})).json()
        start_btn = (await API.Get('get_text', params={'func': 'pool_start', 'variable': 1})).json()
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'after_meet'})
        await msg.answer(text=text.get('text'), reply_markup=inline_keys.get_inl_key([start_btn.get('text')]))

        return None
    await msg.answer(text=text, reply_markup=reply_keys.reply_keyboard_remove)
    await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))


@msgs.message(filters.StateFilterMsg('poll_main'))
async def main_answer(msg: Message):
    answer = (await API.Post('main_answer', data={'id': msg.from_user.id, 'answer': msg.text})).json()
    if answer.get('error'):
        await msg.answer(text=((await API.Get('get_text', params={'func': 'pool_valid_erorr', 'variable': 1})).json()).get('text'))
        question = answer.get('question')
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))

        return None
    #text = answer.get('answer_to_answer')
    question = (await API.Get('get_main_question', params={'tg_id': msg.from_user.id, 'new': False})).json()
    if question.get('main_question'):
        #await msg.answer(text=text)
        question = (await API.Get('get_filter_question', params={'tg_id': msg.from_user.id})).json()
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'poll_filter'})

        return None
    #await msg.answer(text=text)
    await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))


bot2 = Bot(token=API.get_token())


async def get_sug(msg: Message):

    sug_info = (await API.Get('gen_suggestion', params={'tg_id': msg.from_user.id})).json()
    sug = sug_info.get('sug')
    if sug == 'Not Found':
        sug_info = (await API.Get('get_random_sug', params={'tg_id': msg.from_user.id})).json()
        sug = sug_info.get('sug')

    text = ""
    if sug.get('address') != None:
        text = f"<b>{sug.get('title')}</b>\n\n🎯{sug.get('short_desc')}\n\n💵{sug.get('price')}\n\n📍{sug.get('address')}\n\nПредложение: {str(sug_info.get('index'))} из {sug_info.get('len')}"
    else:
        text = f"<b>{sug.get('title')}</b>\n\n🎯{sug.get('short_desc')}\n\n💵{sug.get('price')}\n\nПредложение: {str(sug_info.get('index'))} из {sug_info.get('len')}"
    media = [InputMediaPhoto(media=URLInputFile(
        sug.get('cover')), caption=sug.get('title'))]

    for item in sug.get('images'):
        media.append(InputMediaPhoto(media=URLInputFile(item)))
    while True:
        try:
            msgs = await bot2.send_media_group(msg.from_user.id, media=media, request_timeout=5)
            break
        except:
            pass

    num_list = []
    for msg_id in msgs:

        num_list.append(msg_id.message_id)
    key = (await API.Post('get_photo_name', data={'photo_id': num_list})).json()
    await bot2.send_message(chat_id=msg.from_user.id,
                                    text=text,
                                    parse_mode="HTML",
                                    reply_markup=await inline_keys.get_inl_key_sug(
                                        key=key,
                                        btn={
                                            '⬅️⬅️': 'prev',
                                            'Связаться': f'{sug.get("contact")}',
                                            "➡️➡️": "next",
                                            'Поменять ответы': 'pool'}))


@msgs.message(filters.StateFilterMsg('poll_filter'))
async def filter_answer(msg: Message):
    answer = (await API.Post('filter_answer', data={'id': msg.from_user.id, 'answer': msg.text})).json()
    if answer.get('error'):
        await msg.answer(text=((await API.Get('get_text', params={'func': 'pool_valid_erorr', 'variable': 1})).json()).get('text'))
        question = answer.get('question')
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))

        return None
    text = random.choice(answer.get('answer_to_answer'))

    question = (await API.Get('get_filter_question', params={'tg_id': msg.from_user.id})).json()
    if question.get('filter_question'):
        question = (await API.Get('get_stat_question', params={'tg_id': msg.from_user.id})).json()
        if question.get('session'):
            await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'free'})
            if not (await API.Get('get_user_text_view', params={"tg_id": msg.from_user.id})).json().get('text_view'):
                await msg.answer(text=(await API.Get('get_text', params={'func': 'get_sug_view', 'variable': 3, "tg_id": msg.from_user.id})).json().get('text'), 
                                 reply_markup=reply_keys.reply_keyboard_remove)
                await msg.answer(text=(await API.Get('get_text', params={'func': 'get_sug_view', 'variable': 1, "tg_id": msg.from_user.id})).json().get('text'),
                                 reply_markup=inline_keys.get_inl_key_get(btn=((await API.Get('get_text', params={'func': 'get_sug_view', 'variable': 2, "tg_id": msg.from_user.id})).json()).get('text')))
            else:
                await msg.answer(text=(await API.Get('get_text', params={'func': 'get_sug_view', 'variable': 4, "tg_id": msg.from_user.id})).json().get('text'), 
                                 reply_markup=reply_keys.reply_keyboard_remove)
                await start_sug(msg)
            return None
        await msg.answer(text=text)
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'poll_stats'})

        return None
    await msg.answer(text=text)
    await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))


@msgs.message(filters.StateFilterMsg('poll_stats'))
async def stats_answer(msg: Message):
    answer = (await API.Post('stat_answer', data={'id': msg.from_user.id, 'answer': msg.text})).json()
    if answer.get('error'):
        await msg.answer(text=((await API.Get('get_text', params={'func': 'pool_valid_erorr', 'variable': 1})).json()).get('text'))
        question = answer.get('question')
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))

        return None
    text = random.choice(answer.get('answer_to_answer'))

    question = (await API.Get('get_stat_question', params={'tg_id': msg.from_user.id})).json()
    if question.get('session'):
        await msg.answer(text=text, reply_markup=reply_keys.reply_keyboard_remove)
        if (text_msg := (await API.Get('get_text', params={'func': 'get_sug_view', 'variable': 1, "tg_id" : msg.from_user.id})).json().get('text')) != None:
            await msg.answer(text=text_msg,
                             reply_markup=inline_keys.get_inl_key_get(btn=((await API.Get('get_text', params={'func': 'get_sug_view', 'variable': 2, "tg_id" : msg.from_user.id})).json()).get('text')))
        else:
            await msg.answer(text=(await API.Get('get_text', params={'func': 'get_sug_view', 'variable': 3, "tg_id": msg.from_user.id})).json().get('text'),
                                 reply_markup=inline_keys.get_inl_key_get(btn=((await API.Get('get_text', params={'func': 'get_sug_view', 'variable': 4, "tg_id": msg.from_user.id})).json()).get('text')))
            
       # ms=await msg.answer(text="Загружаем предложения...")
       # await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'free'})
       # await get_sug(msg=msg)
        # await bot2.delete_message(msg.chat.id, ms.message_id)
        return None
    await msg.answer(text=text)
    await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
