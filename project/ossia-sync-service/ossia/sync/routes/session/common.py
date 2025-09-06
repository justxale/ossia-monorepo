
from fastapi import APIRouter

from ossia.sync.schemas.session import CreateSession
from ossia.sync.services.session import SessionService

router = APIRouter()


@router.post('/', )
async def create_session(body: CreateSession):
    state = SessionService.create_session(
        body.permissions.edit, body.permissions.skip, body.playback_type, body.playback_oid
    )
    return state
