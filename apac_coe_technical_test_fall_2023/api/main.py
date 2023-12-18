import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from apac_coe_technical_test_fall_2023.api.routes.commission import (
    router as comission_router,
)
from apac_coe_technical_test_fall_2023.api.routes.login import router as login_router
from apac_coe_technical_test_fall_2023.api.routes.order import router as orders_router
from apac_coe_technical_test_fall_2023.api.routes.trade import router as trade_router

app = FastAPI()

app.include_router(orders_router, prefix="/api")
app.include_router(trade_router, prefix="/api")
app.include_router(comission_router, prefix="/api")
app.include_router(login_router, prefix="/auth")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc.errors())
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )


@app.get("/")
async def main():
    # Redirect to /docs (relative URL)
    return RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)


def start():
    uvicorn.run(app, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
