from fastapi import HTTPException
from starlette import status

from ossia.sync.services.session import SessionState, SessionService


def get_session(session_id: str) -> SessionState:
    try:
        return SessionService.get_session(session_id)
    except KeyError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Session not found')


