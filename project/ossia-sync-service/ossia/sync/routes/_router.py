from fastapi import APIRouter

from .session import session_id, common

router = APIRouter(prefix='/session')
router.include_router(common.router)
router.include_router(session_id.router)

