from aiogram import Router, types, Bot
from aiogram.types import Message, URLInputFile, InputMediaPhoto
from apiNBD import API
from aiogram.filters.command import CommandStart, CommandObject, Command
from botNBD.my_filters import filters
from botNBD.custom_keyboards import inline_keys, reply_keys

cmd = Router()


@cmd.message(CommandStart())
async def command_start_handler(msg: Message, command: CommandObject) -> None:
    exist = await API.Get('exist_user', params={'tg_id': msg.from_user.id})
    if exist.is_client_error:
        data = msg.from_user.dict()
        data['ref_link'] = command.args
        await API.Post('add_user_tg', data=data)
        r = (await API.Get('get_text', params={'func': 'start', 'variable': 1})).json()
        await msg.answer(
            (r.get('text')).format(msg.from_user.first_name),
            reply_markup=inline_keys.get_inl_key({
                ((await API.Get('get_text',
                                params={'func': 'start_btn', 'variable': 1})).json()).get('text'): "start_meet"
            })
        )
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'after_start'})
    elif exist.is_success:
        r = (await API.Get('get_text', params={'func': 'start', 'variable': 2})).json()
        await msg.answer(
            (r.get('text')).format(msg.from_user.first_name),
            reply_markup=inline_keys.get_inl_key([
                ((await API.Get('get_text',
                                params={'func': 'start_btn', 'variable': 1})).json()).get('text')
            ]))
        await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'after_start'})
        # https://t.me/NBDDEVTEST?start=airplane


@cmd.message(Command("bug"), filters.StateUnlockFilter())
async def bug_reg(msg: Message):
    await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'bug'})
    text = (await API.Get('get_text', params={'func': 'bug', 'variable': 1})).json()
    await msg.answer(text.get('text'))




@cmd.message(Command("profile"), filters.StateUnlockFilter())
async def get_profile(msg: Message):
    text = "Ваш профиль:\n"
    profile = (await API.Get('user_profile', params={'tg_id': msg.from_user.id})).json()
    for el in profile:
        text = text+f"{el}: {profile.get(el)}\n"
    await msg.answer(text)


@cmd.message(Command("contact"), filters.StateUnlockFilter())
async def get_contacts(msg: Message):
    text = "наши контакты:\n"
    profile = (await API.Get('get_contact')).json()
    for el in profile:

        text = text+f'{el}\n{profile.get(el)}\n'
        text = text+f'\n'

    await msg.answer(text)


@cmd.message(Command("poll"), filters.StateUnlockFilter())
async def cmd_start_poll(msg: Message):
    if msg.reply_markup:
        await msg.edit_reply_markup(reply_markup=None)
    await API.Post('set_user_state', data={'id': msg.from_user.id, 'state': 'poll_main'})
    question = (await API.Get('get_main_question', params={'tg_id': msg.from_user.id})).json()
    await msg.answer(text=question.get('question'),
                     reply_markup=reply_keys.get_repl_key(question.get('recom_answer')))
