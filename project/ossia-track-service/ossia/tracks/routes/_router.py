from fastapi import APIRouter

from ossia.tracks.routes.broker import router as broker_router
from ossia.tracks.routes.creators import creators_router
from ossia.tracks.routes.tracks import tracks_router

router = APIRouter()
router.include_router(tracks_router)
router.include_router(broker_router)
router.include_router(creators_router)
