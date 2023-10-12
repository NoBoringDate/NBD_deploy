import logging

from aiogram import Bot, Dispatcher, types, Router



class BOT:
    

    def __init__(self, handlers:list[Router], token:str):
        self.dp=Dispatcher()
        for r in handlers:
            self.dp.include_router(r)
        self.bot=Bot(token=token)
        
        
    def start(self):
        try:
            self.dp.run_polling(self.bot, polling_timeout=300)
        except Exception as ex:
            logging.info(f"Bot don't start: {ex}", stack_info=True)