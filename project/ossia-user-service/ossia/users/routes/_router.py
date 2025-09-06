from fastapi import APIRouter

from ossia.users.routes.broker import router as broker_router
from ossia.users.routes.me import router as me_router
from ossia.users.routes.oauth import router as oauth_router

router = APIRouter()

router.include_router(oauth_router)
router.include_router(me_router)
router.include_router(broker_router)
