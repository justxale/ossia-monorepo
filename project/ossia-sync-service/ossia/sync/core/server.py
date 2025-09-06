from fastapi import FastAPI

from ossia.sync.routes import router

app = FastAPI()
app.include_router(router)
