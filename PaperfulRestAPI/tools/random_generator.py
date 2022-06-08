import secrets
from random import randint


def get_six_random_number():
    value = randint(100000, 999999)
    return value


def get_sixteen_random_token():
    value = secrets.token_urlsafe()
    return value
