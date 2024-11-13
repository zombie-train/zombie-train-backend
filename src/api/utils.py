import logging
from functools import lru_cache
from django.db import OperationalError
from django.db.utils import ProgrammingError
from api.models import Region
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os
import telegram


load_dotenv()
logger = logging.getLogger(__name__)

HASH_SCORE_KEY = os.getenv("HASH_SCORE_KEY")
cipher_suite = Fernet(HASH_SCORE_KEY)

TELEGRAM_BOT = None

@lru_cache(maxsize=1)
def get_default_region():
    try:
        return Region.objects.first()
    except OperationalError as e:
        logger.warning(str(e))
    except ProgrammingError as e:
        logger.warning(str(e))
    return None



def unhash_value(hashed_value):
    byte_hashed_value = hashed_value.encode('utf-8')
    try:
        decrypted_value = cipher_suite.decrypt(byte_hashed_value)
        return decrypted_value.decode('utf-8')
    except Exception as e:
        raise ValueError("Invalid hashed value")


def hash_value(value):
    HASH_SCORE_KEY = os.environ["HASH_SCORE_KEY"]
    cipher_suite = Fernet(HASH_SCORE_KEY)
    byte_value = str(value).encode('utf-8')
    hashed_value = cipher_suite.encrypt(byte_value)
    return hashed_value.decode('utf-8')


def get_telegram_bot():
    global TELEGRAM_BOT
    if TELEGRAM_BOT is None:
        TELEGRAM_BOT = telegram.Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    return TELEGRAM_BOT
