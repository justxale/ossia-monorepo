import asyncio
import time

from pulsola.sync.enum import SessionAction, WebsocketStatus
from pulsola.sync.schemas import SyncEvent, ActionEvent, WebsocketResponse
from pulsola.sync.schemas.ws import OnEndEvent
from pulsola.sync.services.session import ListenerState, SessionState


async def send_to_clients(state: SessionState, msg: WebsocketResponse):
    async with asyncio.TaskGroup() as tg:
        for listener in state.listeners.values():
            tg.create_task(
                listener.socket.send_text(msg.model_dump_json())
            )


async def on_action(event: ActionEvent, session: SessionState, state: ListenerState):
    match event.action:
        case SessionAction.PAUSE:
            if session.is_paused:
                return
            elapsed = time.time() - session.started_at
            session.is_paused = True
            session.paused_at = elapsed

        case SessionAction.RESUME:
            if not (session.is_paused and session.paused_at):
                return
            session.is_paused = False
            session.started_at = time.time() - session.paused_at

    msg = WebsocketResponse(event=event, code=WebsocketStatus.OK)
    await send_to_clients(session, msg)
    # TODO: NEXT, SEEK and PREVIOUS actions


async def on_sync(_: SyncEvent, session: SessionState, state: ListenerState):
    elapsed = time.time() - session.started_at
    msg = WebsocketResponse(event=SyncEvent(elapsed=elapsed), code=WebsocketStatus.OK)
    await state.socket.send_text(msg.model_dump_json())


async def on_end(event: OnEndEvent, session: SessionState, state: ListenerState):
    pass
