import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from tortoise.contrib.fastapi import RegisterTortoise

from ossia.tracks.config import TracksServiceConfig
from ossia.tracks.database import models
from ossia.tracks.routes import router
from ossia.tracks.services.s3 import Buckets, S3Service
from ossia.tracks.telemetry import (
    counter_middleware,
    duration_middleware,
    telemetry_setup,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with S3Service() as s3:
        await asyncio.gather(
            *[s3.create_bucket(Bucket=bucket) for bucket in Buckets.all_buckets()],
            return_exceptions=True,
        )

    db_url = TracksServiceConfig().postgres_dsn
    async with RegisterTortoise(
            app=app, modules={'ossia': [models]}, db_url=db_url, generate_schemas=True
    ):
        yield


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    root_path='/api/v1',
    docs_url='/tracks/docs',
    openapi_url='/tracks/openapi.json',
)
if not TracksServiceConfig().disable_telemetry:
    telemetry_setup(app)
    app.middleware('http')(duration_middleware)
    app.middleware('http')(counter_middleware)

app.include_router(router)


@app.exception_handler(RequestValidationError)
def handle_validation(request: Request, exc: RequestValidationError):
    print(exc)
