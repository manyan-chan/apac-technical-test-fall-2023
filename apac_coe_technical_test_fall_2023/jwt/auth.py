import jwt
from fastapi.security import OAuth2PasswordBearer

from apac_coe_technical_test_fall_2023.settings import (
    APP_PASSWORD,
    APP_USERNAME,
    SECRET_KEY,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def generate_token(payload: dict) -> str:
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


SAMPLE_USER_TOKEN = generate_token({"username": APP_USERNAME, "password": APP_PASSWORD})

def verify_token(token: str) -> bool:
    try:
        return token == SAMPLE_USER_TOKEN
    except Exception:
        return False
