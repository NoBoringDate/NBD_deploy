from aiogram import Router
from aiogram.filters import Filter
from aiogram.types import Message
from apiNBD import API
router = Router()


class StateFilter(Filter):
    def __init__(self, state: str) -> None:
        self.my_text = state


class StateUnlockFilter(Filter):
    async def __call__(self, message: Message):
        state = (await API.Get('get_user_state', params={'id': message.from_user.id})).json()

        if (state.get('curent_state') != 'after_start')\
                and (state.get('curent_state') != 'meet') \
                and (state.get('curent_state') != 'poll_main') \
                and (state.get('curent_state') != 'poll_filter'):
            return True
        else:
            return False


class StateFilter(Filter):
    def __init__(self, state: str) -> None:
        self.state = state

    async def __call__(self, msg: Message) -> bool:
        return self.state == ((
                                    await API.Get('get_user_state',
                                    params={'id': msg.from_user.id})
                                ).json()).get('curent_state')


def StateFilterFn():
    pass