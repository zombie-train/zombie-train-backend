import os
from pprint import pprint

import requests
from cryptography.fernet import Fernet

from dotenv import load_dotenv

load_dotenv()

TOKEN = None


def salt_value(value):
    SALTY_COEFFICIENT = int(os.environ["SALTY_COEFFICIENT"])
    return value * SALTY_COEFFICIENT


def hash_value(value):
    HASH_SCORE_KEY = os.environ["HASH_SCORE_KEY"]
    cipher_suite = Fernet(HASH_SCORE_KEY)
    byte_value = str(value).encode('utf-8')
    hashed_value = cipher_suite.encrypt(byte_value)
    return hashed_value.decode('utf-8')


def generate_token():
    if globals()["TOKEN"]:
        return globals()["TOKEN"]
    username = os.environ["ADMIN_USERNAME"]
    password = os.environ["ADMIN_PASSWORD"]
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    payload = (f'grant_type=password'
               f'&username={username}'
               f'&password={password}'
               f'&client_id={client_id}'
               f'&client_secret={client_secret}')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    r = requests.post(
        url="http://127.0.0.1:8000/o/token/",
        headers=headers,
        data=payload
    )

    r.raise_for_status()
    globals()["TOKEN"] = r.json()["access_token"]
    return globals()["TOKEN"]


def test_get_users():
    token = generate_token()
    print(f"Token: {token}")
    r = requests.get("http://127.0.0.1:8000/api/users/",
                     headers={
                         "Authorization": f"Bearer {token}"
                     })
    pprint(r.json())


def test_get_scores():
    token = generate_token()
    print(f"Token: {token}")
    r = requests.get("http://127.0.0.1:8000/api/scores/",
                     headers={
                         "Authorization": f"Bearer {token}"
                     })
    pprint(r.json())


def test_get_leaderboard():
    r = requests.get("http://127.0.0.1:8000/api/leaderboard/",
                     params={
                         # "date":str(date.today())
                         "score_date": "2024-05-24"
                     })
    pprint(r.json())


def test_get_profile():
    token = generate_token()
    print(f"Token: {token}")
    r = requests.get("http://127.0.0.1:8000/api/profile/",
                     params={
                         "token": token
                     },
                     headers={
                         "Authorization": f"Bearer {token}"
                     })
    pprint(r.json())


def test_create_score():
    score = 120
    salted_score = salt_value(score)
    hashed_value = hash_value(salted_score)
    token = generate_token()
    print(f"Token: {token}")
    r = requests.post("http://127.0.0.1:8000/api/scores/",
                      headers={
                          "Authorization": f"Bearer {token}"
                      },
                      json={"hashed_value": hashed_value, }
                      )

    pprint(r.text)


def test_create_user():
    api_key = "common_api_key"
    user_id = 0
    score = 111
    timestamp, token = generate_token(user_id, score, api_key)
    print(f"Timestamp: {timestamp}, Token: {token}")
    r = requests.post(
        "http://127.0.0.1:8000/users/",
        params={
            "token": token
        },
        json={
            "username": "created_user",
        }
    )
    pprint(r.text)


if __name__ == '__main__':
    test_get_scores()
    # test_get_leaderboard()
    # test_create_user()
    # test_create_score()
    # test_get_users()
    # test_get_profile()
