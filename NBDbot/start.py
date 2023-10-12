
import logging

from apiNBD import API
from botNBD import BOT
from botNBD.handlers import cmd_handler, msg_handlers, clb_handlers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",)
bot = BOT(handlers=[cmd_handler.cmd, msg_handlers.msgs, clb_handlers.clbs ], token=API.get_token())

bot.start()
