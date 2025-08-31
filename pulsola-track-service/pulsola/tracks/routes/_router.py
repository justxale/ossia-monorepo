from fastapi import APIRouter

from pulsola.tracks.routes.broker import router as broker_router
from pulsola.tracks.routes.creators import creators_router
from pulsola.tracks.routes.tracks import tracks_router

router = APIRouter()
router.include_router(tracks_router)
router.include_router(broker_router)
router.include_router(creators_router)
