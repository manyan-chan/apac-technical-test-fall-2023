import datetime as dt
import math
from decimal import Decimal
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import DatabaseError, OperationalError

from apac_coe_technical_test_fall_2023.api.pagination import Pagination, paginate
from apac_coe_technical_test_fall_2023.database.connection import Session
from apac_coe_technical_test_fall_2023.jwt.auth import oauth2_scheme, verify_token
from apac_coe_technical_test_fall_2023.model.mysql import Trades

router = APIRouter()
session = Session()


class GetComissionQueryParams:
    def __init__(
        self,
        page: int = Query(
            1,
            ge=1,
            description="Page number, default = 1",
        ),
        limit: int = Query(
            15,
            ge=1,
            description="Number of results per page, default = 15",
        ),
    ):
        self.page = page
        self.limit = limit


class GetComissionResponseModel(BaseModel):
    status: int
    data: list[dict] | str
    timestamp: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    pagination: Optional[Pagination] = None


def get_comission(row: pd.Series):
    if row["Commission_Type"] == "FIXED_AMOUNT":
        return row["Commission_Value"]
    elif row["Commission_Type"] == "bps":
        value = (
            Decimal(row["Commission_Value"])
            * Decimal(row["Gross_Consideration"])
            / 10000
        )
        return str(value)
    else:
        return 0


@router.get("/getComission")
def get_trade(
    query_params: GetComissionQueryParams = Depends(GetComissionQueryParams),
    token: str = Depends(oauth2_scheme),
) -> JSONResponse:
    try:
        # Verify the token
        if not verify_token(token):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=GetComissionResponseModel(
                    status=status.HTTP_401_UNAUTHORIZED, data="Unauthorized"
                ).model_dump(),
            )

        # Create the query
        query = session.query(Trades)

        # Paginate the query
        paginated_query = paginate(query, query_params.page, query_params.limit)
        results = paginated_query.all()

        if not results:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=GetComissionResponseModel(
                    status=status.HTTP_404_NOT_FOUND, data=[]
                ).model_dump(),
            )

        total_results = query.count()
        total_pages = math.ceil(total_results / query_params.limit)
        next_page = query_params.page + 1 if query_params.page < total_pages else None
        prev_page = query_params.page - 1 if query_params.page > 1 else None

        pagination = Pagination(
            total=total_results,
            currentPage=query_params.page,
            totalPages=total_pages,
            nextPage=next_page,
            prevPage=prev_page,
        )

        df = pd.DataFrame([trade.to_dict() for trade in results])
        df["Commission"] = df.apply(get_comission, axis=1)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=GetComissionResponseModel(
                status=status.HTTP_200_OK,
                data=df.to_dict("records"),
                pagination=pagination,
            ).model_dump(),
        )

    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=GetComissionResponseModel(
                status=status.HTTP_400_BAD_REQUEST, data="Bad request"
            ).model_dump(),
        )
    except (DatabaseError, OperationalError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=GetComissionResponseModel(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data="Internal server error",
            ).model_dump(),
        )
