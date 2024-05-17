import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from pprint import pprint

import requests


def generate_token(user_id, score, api_key):
    timestamp = int(datetime.now().timestamp())
    message = f"{timestamp}{user_id}{score}"
    signature = hmac.new(api_key.encode(), message.encode(),
                         hashlib.sha256).hexdigest()

    # Concatenate all key parts
    token_parts = f"{timestamp}:{user_id}:{score}:{signature}"

    # Base64 encode the token
    token = base64.b64encode(token_parts.encode()).decode()
    return timestamp, token


def test_get_users():
    api_key = "common_api_key"
    user_id = 123
    score = 100
    timestamp, token = generate_token(user_id, score, api_key)
    print(f"Timestamp: {timestamp}, Token: {token}")
    r = requests.get("http://127.0.0.1:8000/api/users/",
                     params={
                         "token": token
                     })
    pprint(r.json())


def test_get_scores():
    api_key = "common_api_key"
    user_id = 123
    score = 100
    timestamp, token = generate_token(user_id, score, api_key)
    print(f"Timestamp: {timestamp}, Token: {token}")
    r = requests.get("http://127.0.0.1:8000/api/scores/",
                     params={
                         "token": token,
                         # "score_date": '2024-05-15'
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
    test_get_scores()
    # test_create_user()
    # test_create_score()
    # test_get_users()