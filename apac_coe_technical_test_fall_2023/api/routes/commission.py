import datetime as dt
from decimal import Decimal

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import DatabaseError, OperationalError

from apac_coe_technical_test_fall_2023.database.connection import Session
from apac_coe_technical_test_fall_2023.jwt.auth import oauth2_scheme, verify_token
from apac_coe_technical_test_fall_2023.model.mysql import Trades

router = APIRouter()
session = Session()


class GetCommissionResponseModel(BaseModel):
    status: int
    data: list[dict] | str
    timestamp: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )


def get_commission(trade: dict):
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
        return 0


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

        # Create the query
        query = session.query(Trades)
        results = query.all()

        if not results:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=GetCommissionResponseModel(
                    status=status.HTTP_404_NOT_FOUND, data=[]
                ).model_dump(),
            )

        trades = [trade.to_dict() for trade in results]
        for trade in trades:
            trade["Commission"] = get_commission(trade)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=GetCommissionResponseModel(
                status=status.HTTP_200_OK,
                data=trades,
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
