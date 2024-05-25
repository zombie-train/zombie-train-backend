import os
from datetime import datetime, timedelta, date
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = None


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
    token = generate_token()
    print(f"Token: {token}")
    r = requests.get("http://127.0.0.1:8000/api/leaderboard/",
                     params={
                         # "date":str(date.today())
                         "score_date": "2024-05-24"
                     },
                     headers={
                         "Authorization": f"Bearer {token}"
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
    api_key = "common_api_key"
    user_id = 3
    score = 100
    timestamp, token = generate_token(user_id, score, api_key)
    print(f"Timestamp: {timestamp}, Token: {token}")
    r = requests.post("http://127.0.0.1:8000/api/scores/",
                      params={
                          "token": token
                      },
                      json={"points": 100,
                            "score_ts": str(datetime.now() - timedelta(days=2)),
                            "user_id": user_id}
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
    # test_get_scores()
    test_get_leaderboard()
    # test_create_user()
    # test_create_score()
    # test_get_users()
    # test_get_profile()
