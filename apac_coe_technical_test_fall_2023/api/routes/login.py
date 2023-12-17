import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from apac_coe_technical_test_fall_2023.jwt.auth import SAMPLE_USER_TOKEN, generate_token

router = APIRouter()


class LoginResponse(BaseModel):
    status: int
    data: dict | str
    timestamp: str = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> JSONResponse:
    token = generate_token(
        {"username": form_data.username, "password": form_data.password}
    )
    if token == SAMPLE_USER_TOKEN:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=LoginResponse(
                status=status.HTTP_200_OK,
                data={"token": token},
            ).model_dump(),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=LoginResponse(
                status=status.HTTP_401_UNAUTHORIZED, data="Unauthorized"
            ).model_dump(),
        )
