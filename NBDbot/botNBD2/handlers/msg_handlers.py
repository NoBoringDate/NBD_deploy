import random

from aiogram import Router, Bot
from aiogram.types import Message, InputMediaPhoto, URLInputFile
from apiNBD import API
from botNBD.custom_keyboards import reply_keys, inline_keys
from botNBD.my_filters import filters
import json
msgs = Router()


@msgs.message(filters.StateFilter('bug'))
async def echo_handler(msg: Message) -> None:
    await API.Get('bug_report', params={'tg_id': msg.from_user.id, "bug_report": msg.text})
    text = (await API.Get('get_text', params={'func': 'bug', 'variable': 2})).json()
    await msg.answer((text.get('text')).format(msg.from_user.first_name))
    await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'free'})


@msgs.message(filters.StateFilter('meet'))
async def meet_answer(msg: Message):
    tag = (await API.Get('get_tag', params={'tg_id': msg.from_user.id})).json()
    answer = (await API.Post('meet_answer', data={'id': msg.from_user.id, tag.get('tag'): msg.text})).json()
    if answer.get('error'):
        await msg.answer(text = ((await API.Get('get_text', params={'func': 'age_valid_erorr', 'variable': 1})).json()).get('text'))
        question = answer.get('question')
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))

        return None
    text = random.choice(answer.get('answer_to_answer'))
    await msg.answer(text=text, reply_markup=reply_keys.reply_keyboard_remove)
    question = (await API.Get('get_meet_question', params={'tg_id': msg.from_user.id})).json()
    if question.get('session'):
        text = (await API.Get('get_text', params={'func': 'meet_end', 'variable': 1})).json()
        start_btn=(await API.Get('get_text', params={'func': 'pool_start', 'variable': 1})).json()
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'after_meet'})
        await msg.answer(text=text.get('text'), reply_markup=inline_keys.get_inl_key([start_btn.get('text')]))

        return None
    await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))


@msgs.message(filters.StateFilter('poll_main'))
async def main_answer(msg: Message):
    answer = (await API.Post('main_answer', data={'id': msg.from_user.id, 'answer': msg.text})).json()
    if answer.get('error'):
        await msg.answer(text=((await API.Get('get_text', params={'func': 'pool_valid_erorr', 'variable': 1})).json()).get('text'))
        question = answer.get('question')
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))

        return None
    text = answer.get('answer_to_answer')
    await msg.answer(text=text, reply_markup=reply_keys.reply_keyboard_remove)
    question = (await API.Get('get_main_question', params={'tg_id': msg.from_user.id})).json()
    if question.get('main_question'):
        question = (await API.Get('get_filter_question', params={'tg_id': msg.from_user.id})).json()
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'poll_filter'})

        return None

    await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))


bot2 = Bot(token=API.get_token())


async def get_sug(msg: Message):

    sug_info = (await API.Get('gen_suggestion', params={'tg_id': msg.from_user.id})).json()
    sug = sug_info.get('sug')
    if sug == 'Not Found':
        sug_info = (await API.Get('get_random_sug', params={'tg_id': msg.from_user.id})).json()
        sug = sug_info.get('sug')

    text = f"{sug.get('description')}\n\n{sug.get('price')}\n\nПредложение: {str(sug_info.get('index'))} из {sug_info.get('len')}"
    media = [InputMediaPhoto(media=URLInputFile(sug.get('cover')), caption=sug.get('title'))]

    for item in sug.get('images'):
        media.append(InputMediaPhoto(media=URLInputFile(item)))
    msgs = await bot2.send_media_group(msg.from_user.id, media=media)

    await msg.answer(text=text, reply_markup=inline_keys.get_inl_key_sug(
        title_id=msgs,
        btn={
            '<--': 'prev',
            'Ссылка': f'{sug.get("contact")}',
            "-->": "next",
            'Поменять ответы':'pool'}))


@msgs.message(filters.StateFilter('poll_filter'))
async def filter_answer(msg: Message):
    answer = (await API.Post('filter_answer', data={'id': msg.from_user.id, 'answer': msg.text})).json()
    if answer.get('error'):
        await msg.answer(text=(await API.Get('get_text', params={'func': 'pool_valid_erorr', 'variable': 1})).json())
        question = answer.get('question')
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))

        return None
    text = random.choice(answer.get('answer_to_answer'))
    await msg.answer(text=text, reply_markup=reply_keys.reply_keyboard_remove)
    question = (await API.Get('get_filter_question', params={'tg_id': msg.from_user.id})).json()
    if question.get('filter_question'):

        question = (await API.Get('get_stat_question', params={'tg_id': msg.from_user.id})).json()
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'poll_stats'})

        return None

    await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))


@msgs.message(filters.StateFilter('poll_stats'))
async def stats_answer(msg: Message):
    answer = (await API.Post('stat_answer', data={'id': msg.from_user.id, 'answer': msg.text})).json()
    if answer.get('error'):
        await msg.answer(text=(await API.Get('get_text', params={'func': 'pool_valid_erorr', 'variable': 1})).json())
        question = answer.get('question')
        await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))

        return None
    text = random.choice(answer.get('answer_to_answer'))
    await msg.answer(text=text, reply_markup=reply_keys.reply_keyboard_remove)
    question = (await API.Get('get_stat_question', params={'tg_id': msg.from_user.id})).json()
    if question.get('session'):

        ms=await msg.answer(text="Загружаем предложения...")
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'free'})
        await get_sug(msg=msg)
        await bot2.delete_message(msg.chat.id, ms.message_id)
        return None

    await msg.answer(text=question.get('question'), reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))