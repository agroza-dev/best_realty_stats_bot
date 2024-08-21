import logging
import os
from logging.handlers import TimedRotatingFileHandler
from config import config


def setup_logging():
    log_dir = config.Store.LOGS_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'bot.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8')
    handler.suffix = "%d-%m-%Y"
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log


logger = setup_logging()
