import datetime as dt
import math
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import DatabaseError, OperationalError

from apac_coe_technical_test_fall_2023.api.pagination import Pagination, paginate
from apac_coe_technical_test_fall_2023.database.connection import Session
from apac_coe_technical_test_fall_2023.jwt.auth import oauth2_scheme, verify_token
from apac_coe_technical_test_fall_2023.model.mysql import Orders

router = APIRouter()
session = Session()


class GetOrderQueryParams:
    def __init__(
        self,
        date: Optional[str] = Query(
            None,
            description="Search for Entered_Datetime in YYYY-MM-DD format",
        ),
        buySell: Optional[str] = Query(
            None,
            description="Search for Buy_Sell (B or S)",
        ),
        topLevel: Optional[str] = Query(
            None,
            description="Search for Top_Level (Y or N)",
        ),
        ticker: Optional[str] = Query(
            None,
            description="Search for Instrument_Code",
        ),
        counterparty: Optional[str] = Query(
            None,
            description="Search for Counterparty_Code",
        ),
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
        self.date = date
        self.buySell = buySell
        self.topLevel = topLevel
        self.ticker = ticker
        self.counterparty = counterparty
        self.page = page
        self.limit = limit

    def validate_date(self):
        if self.date:
            try:
                dt.datetime.strptime(self.date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format, should be YYYY-MM-DD")

    def validate_buySell(self):
        if self.buySell and self.buySell not in ["B", "S"]:
            raise ValueError("Invalid buySell value, should be B or S")

    def validate_topLevel(self):
        if self.topLevel and self.topLevel not in ["Y", "N"]:
            raise ValueError("Invalid topLevel value, should be Y or N")


class GetOrderResponseModel(BaseModel):
    status: int
    data: list[dict] | str
    timestamp: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    pagination: Optional[Pagination] = None


@router.get("/getOrder")
def get_order(
    query_params: GetOrderQueryParams = Depends(GetOrderQueryParams),
    token: str = Depends(oauth2_scheme),
) -> JSONResponse:
    try:
        if not verify_token(token):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=GetOrderResponseModel(
                    status=status.HTTP_401_UNAUTHORIZED, data="Unauthorized"
                ).model_dump(),
            )

        query = session.query(Orders)

        if query_params.date and query_params.validate_date():
            date = dt.datetime.strptime(query_params.date, "%Y-%m-%d").date()
            query = query.filter(
                Orders.Entered_Datetime >= date,
                Orders.Entered_Datetime < date + dt.timedelta(days=1),
            )

        if query_params.buySell and query_params.validate_buySell():
            query = query.filter(Orders.Buy_Sell == query_params.buySell)

        if query_params.topLevel and query_params.validate_topLevel():
            query = query.filter(Orders.Top_Level == query_params.topLevel)

        if query_params.ticker:
            query = query.filter(Orders.Instrument_Code == query_params.ticker)

        if query_params.counterparty:
            query = query.filter(Orders.Counterparty_Code == query_params.counterparty)

        paginated_query = paginate(query, query_params.page, query_params.limit)
        results: list[Orders] = paginated_query.all()

        if not results:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=GetOrderResponseModel(
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

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=GetOrderResponseModel(
                status=status.HTTP_200_OK,
                data=[order.to_dict() for order in results],
                pagination=pagination,
            ).model_dump(),
        )

    except (DatabaseError, OperationalError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=GetOrderResponseModel(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data="Internal Server Error",
            ).model_dump(),
        )

    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=GetOrderResponseModel(
                status=status.HTTP_400_BAD_REQUEST, data="Bad Request"
            ).model_dump(),
        )
