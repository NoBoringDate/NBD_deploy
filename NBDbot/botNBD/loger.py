from loguru import logger


def info_only(record):
    return record["level"].name == "INFO"


logger.remove()
logger.add("logs/log_{time:DD-MM-YYYY}.log", rotation="00:00", retention="1 months", filter=info_only,
           format="{time:HH:mm:ss} | {level} | <level>{message}</level>")
logger.add("logs/log_error_{time:DD-MM-YYYY}.log", rotation="00:00", retention="1 months", level=30,
           format="{time:HH:mm:ss} | {level} | <level>{message}</level>")
