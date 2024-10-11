import os

import environ
from cryptography.fernet import Fernet

from zombie_train_backend.settings import BASE_DIR

env = environ.Env(
    # Set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
HASH_SCORE_KEY = env("HASH_SCORE_KEY")
SALTY_COEFFICIENT = int(env("SALTY_COEFFICIENT"))
MAX_KILLED_ZOMBIES_PER_MINUTE = int(env("MAX_KILLED_ZOMBIES_PER_MINUTE"))
cipher_suite = Fernet(HASH_SCORE_KEY)


def unhash_value(hashed_value):
    byte_hashed_value = hashed_value.encode('utf-8')
    try:
        decrypted_value = cipher_suite.decrypt(byte_hashed_value)
        return int(decrypted_value.decode('utf-8'))
    except Exception as e:
        raise ValueError("Invalid hashed value")


def unsalt_value(salted_value):
    return salted_value // SALTY_COEFFICIENT
