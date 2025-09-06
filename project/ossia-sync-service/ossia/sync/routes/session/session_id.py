import asyncio
from typing import Annotated

from fastapi import APIRouter, WebSocketException
from fastapi.params import Depends
from pydantic import ValidationError
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from ossia.sync.dependencies.common import get_session
from ossia.sync.dependencies.security import User, optionally_auth_user
from ossia.sync.enum import EventType, WebsocketStatus
from ossia.sync.schemas import WebsocketMessage, WebsocketResponse, OnConnectEvent
from ossia.sync.schemas.session import SessionInfo
from ossia.sync.schemas.ws import WebsocketError
from ossia.sync.services.session import SessionState, SessionService, ListenerState
from ossia.sync.ws.events import on_action, on_sync, on_end

router = APIRouter(prefix='/{session_id}')


@router.get('/')
async def get_session(session: Annotated[SessionState, Depends(get_session)]) -> SessionInfo:
    return SessionInfo.model_validate(session, from_attributes=True)


async def on_event(message: WebsocketMessage, session_state: SessionState, client_state: ListenerState):
    match message.event.event_type:
        case EventType.ACTION:
            await on_action(message.event, session_state, client_state)
        case EventType.SYNC:
            await on_sync(message.event, session_state, client_state)
        case EventType.ON_END:
            await on_end(message.event, session_state, client_state)


@router.websocket('/')
async def listen_to_session(
        ws: WebSocket, session: Annotated[SessionState, Depends(get_session)],
        user: Annotated[User | None, Depends(optionally_auth_user)]
):
    state: ListenerState | None = None
    service = SessionService(session)
    try:
        await ws.accept()

        try:
            parsed = WebsocketMessage.model_validate(await ws.receive_json())
            if parsed.event.event_type != EventType.ON_CONNECT:
                raise ValueError()

            state = service.attach_client(user, ws)

            response = WebsocketResponse(event=OnConnectEvent(client_id=state.encoded_id), code=WebsocketStatus.OK)
            await ws.send_json(response.model_dump_json())
        except (ValidationError, ValueError):
            raise WebSocketException(status.WS_1008_POLICY_VIOLATION, 'Invalid auth packet received')

        async for msg in ws.iter_json():
            try:
                parsed = WebsocketMessage.model_validate(msg)
                if not parsed.client_id:
                    await ws.send_text(
                        WebsocketError(msg="Unauthorized", code=WebsocketStatus.UNAUTHORIZED).model_dump_json()
                    )
                    continue
                state = service.get_client_state(parsed.client_id)
                await on_event(parsed, session, state)
            except ValidationError:
                continue
    except WebSocketDisconnect:
        if state:
            service.detach_client(state.encoded_id)
        return
