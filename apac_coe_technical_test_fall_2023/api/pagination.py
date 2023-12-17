from pydantic import BaseModel
from sqlalchemy.orm import Query
from typing import Optional


class Pagination(BaseModel):
    total: int
    currentPage: int
    totalPages: int
    nextPage: Optional[int] = None
    prevPage: Optional[int] = None


def paginate(query: Query, page: int, limit: int) -> Query:
    return query.limit(limit).offset((page - 1) * limit)
