import datetime as dt

import jwt
from fastapi.security import OAuth2PasswordBearer

from apac_coe_technical_test_fall_2023.settings import (
    APP_PASSWORD,
    APP_USERNAME,
    SECRET_KEY,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def generate_expired_token(payload: dict) -> str:
    expiration_time = dt.datetime.now() - dt.timedelta(minutes=10)
    payload["exp"] = expiration_time.timestamp()
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def generate_token(payload: dict) -> str:
    expiration_time = dt.datetime.now() + dt.timedelta(minutes=10)
    payload["exp"] = expiration_time.timestamp()
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> bool:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expiration_time = decoded_token["exp"]
        username = decoded_token["username"]
        password = decoded_token["password"]
        return (
            username == APP_USERNAME
            and password == APP_PASSWORD
            and dt.datetime.now().timestamp() < expiration_time
        )
    except Exception:
        return False


SAMPLE_USER_TOKEN = generate_token({"username": APP_USERNAME, "password": APP_PASSWORD})
SAMPLE_EXPIRED_TOKEN = generate_expired_token(
    {"username": APP_USERNAME, "password": APP_PASSWORD}
)
