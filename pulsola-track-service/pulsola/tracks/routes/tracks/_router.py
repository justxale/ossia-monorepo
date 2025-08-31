from fastapi import APIRouter

from pulsola.tracks.routes.tracks.common import router as common_router
from pulsola.tracks.routes.tracks.track_id import router as track_id_router

router = APIRouter(prefix='/tracks', tags=['tracks'])

router.include_router(common_router)
router.include_router(track_id_router)
