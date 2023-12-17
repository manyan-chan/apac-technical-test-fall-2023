import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from apac_coe_technical_test_fall_2023.jwt.auth import SAMPLE_USER_TOKEN, generate_token

router = APIRouter()


@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> JSONResponse:
    token = generate_token(
        {"username": form_data.username, "password": form_data.password}
    )
    if token == SAMPLE_USER_TOKEN:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": status.HTTP_200_OK,
                "data": {"token": token},
                "timestamp": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "access_token": token,
                "token_type": "Bearer",
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status": status.HTTP_401_UNAUTHORIZED,
                "data": "Unauthorized",
                "timestamp": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            },
        )
