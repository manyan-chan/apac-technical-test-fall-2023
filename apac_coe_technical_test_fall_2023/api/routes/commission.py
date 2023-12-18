import datetime as dt
from decimal import Decimal

import pandas as pd
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import DatabaseError, OperationalError

from apac_coe_technical_test_fall_2023.database.connection import Session
from apac_coe_technical_test_fall_2023.jwt.auth import oauth2_scheme, verify_token
from apac_coe_technical_test_fall_2023.model.mysql import Orders, Trades

router = APIRouter()
session = Session()


class GetCommissionResponseModel(BaseModel):
    status: int
    data: dict | str
    timestamp: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )


def get_traded_commission(trade: dict):
    if trade["Commission_Type"] == "FIXED_AMOUNT":
        return trade["Commission_Value"]
    elif trade["Commission_Type"] == "bps":
        value = (
            Decimal(trade["Commission_Value"])
            * Decimal(trade["Gross_Consideration"])
            / 10000
        )
        return str(value)
    else:
        return "0"


def get_expected_commission(order: pd.Series):
    if order["Commission_Type"] == "FIXED_AMOUNT":
        return order["Commission_Value"]
    elif order["Commission_Type"] == "bps":
        value = (
            Decimal(order["Commission_Value"])
            * Decimal(order["Quantity_Available"])
            * Decimal(order["Limit_Price"])
            / 10000
        )
        return str(abs(value))
    return "0"


@router.get("/getCommission")
def get_trade(
    token: str = Depends(oauth2_scheme),
) -> JSONResponse:
    try:
        # Verify the token
        if not verify_token(token):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=GetCommissionResponseModel(
                    status=status.HTTP_401_UNAUTHORIZED, data="Unauthorized"
                ).model_dump(),
            )

        trades = session.query(Trades).all()
        orders = session.query(Orders).all()

        if not trades or not orders:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=GetCommissionResponseModel(
                    status=status.HTTP_404_NOT_FOUND, data={}
                ).model_dump(),
            )

        orders = [order.to_dict() for order in orders]
        df_order = pd.DataFrame(orders)
        df_order = df_order.drop_duplicates(subset=["Order_Id"], keep="last")

        # I guess 'C' means cancelled, and 'I' means in progress
        df_order = df_order[df_order.Order_State == "I"]
        df_order["Commission"] = df_order.apply(get_expected_commission, axis=1)

        trades = [trade.to_dict() for trade in trades]
        for trade in trades:
            trade["Commission"] = get_traded_commission(trade)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=GetCommissionResponseModel(
                status=status.HTTP_200_OK,
                data={"trades": trades, "orders": df_order.to_dict(orient="records")},
            ).model_dump(),
        )

    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=GetCommissionResponseModel(
                status=status.HTTP_400_BAD_REQUEST, data="Bad request"
            ).model_dump(),
        )
    except (DatabaseError, OperationalError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=GetCommissionResponseModel(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data="Internal server error",
            ).model_dump(),
        )
