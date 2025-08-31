from fastapi import FastAPI

from pulsola.sync.routes import router

app = FastAPI()
app.include_router(router)
