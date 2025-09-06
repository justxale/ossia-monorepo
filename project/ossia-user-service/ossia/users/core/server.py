from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from tortoise.contrib.fastapi import RegisterTortoise

from ossia.users.config import UserServiceConfig
from ossia.users.database import models
from ossia.users.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = UserServiceConfig()

    async with RegisterTortoise(
            db_url=config.postgres_url, modules={'models': [models.__name__]},
            generate_schemas=True, app=app
    ):
        yield


app = FastAPI(
    default_response_class=ORJSONResponse, lifespan=lifespan,
    root_path='/api/v1'
)
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        content={'status': 'error', 'message': str(exc.detail)},
        status_code=exc.status_code,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> ORJSONResponse:
    return ORJSONResponse(
        content={
            'status': 'error',
            'message': '; '.join(
                [
                    f'{"-> ".join(map(str, error.get("loc", tuple())))}: {error.get("msg", "")}'
                    for error in exc.errors()
                ]
            ),
        },
        status_code=400,
    )
