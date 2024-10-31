import os

from zombie_train_backend import settings
from dotenv import load_dotenv


load_dotenv()

env = settings.ENV

HASH_SCORE_KEY = os.getenv("HASH_SCORE_KEY")
SALTY_COEFFICIENT = int(os.getenv("SALTY_COEFFICIENT"))
MAX_KILLED_ZOMBIES_PER_MINUTE = int(os.getenv("MAX_KILLED_ZOMBIES_PER_MINUTE"))


def unsalt_value(salted_value):
    return salted_value // SALTY_COEFFICIENT
