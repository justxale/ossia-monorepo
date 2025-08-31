from fastapi import APIRouter

from pulsola.users.routes.broker import router as broker_router
from pulsola.users.routes.me import router as me_router
from pulsola.users.routes.oauth import router as oauth_router

router = APIRouter()

router.include_router(oauth_router)
router.include_router(me_router)
router.include_router(broker_router)
