from fastapi import APIRouter

from ossia.tracks.routes.creators.common import router as common_router
from ossia.tracks.routes.creators.creator_id import router as creator_router
from ossia.tracks.routes.creators.creator_tracks import router as tracks_router

router = APIRouter(prefix='/creators', tags=['creators'])
router.include_router(common_router)
router.include_router(creator_router)
router.include_router(tracks_router)
