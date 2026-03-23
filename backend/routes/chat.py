from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from config import get_settings
from models.schemas import ChatMessage
from services.llm_service import stream_chat_completion
from services.memory_service import session_store
from utils.rate_limiter import enforce_rate_limit_ip, get_client_ip_ws
from utils.sanitize import sanitize_user_input


router = APIRouter()
settings = get_settings()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    temperature: Optional[float] = Query(
        None, ge=settings.MIN_TEMPERATURE, le=settings.MAX_TEMPERATURE
    ),
    max_tokens: Optional[int] = Query(
        None, ge=settings.MIN_MAX_TOKENS, le=settings.MAX_MAX_TOKENS
    ),
):
    """
    WebSocket endpoint for chat.

    Protocol:
    - Client connects to `/ws/chat/{session_id}?temperature=...&max_tokens=...`
    - After connection is accepted, client sends plain text messages (JSON not required).
    - Server responds by streaming assistant tokens as text frames.
    - When a response is finished, server sends an empty string `""` as an end-of-response marker.
    """
    # Basic IP rate limiting at connection time
    try:
        client_ip = get_client_ip_ws(websocket)
        enforce_rate_limit_ip(client_ip)
    except Exception:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Rate limit exceeded.",
        )
        return

    await websocket.accept()

    try:
        while True:
            try:
                user_text = await websocket.receive_text()
            except WebSocketDisconnect:
                break

            user_text = sanitize_user_input(user_text)
            if not user_text:
                # Ignore empty messages
                continue

            # Record user message in session history
            session_store.append_message(
                session_id,
                ChatMessage(role="user", content=user_text),
            )

            history = session_store.get_session_messages(session_id)

            # Stream response from the LLM and send each chunk to the client
            try:
                assistant_chunks: list[str] = []
                async for chunk_text in stream_chat_completion(
                    user_message=user_text,
                    history=history,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ):
                    assistant_chunks.append(chunk_text)
                    await websocket.send_text(chunk_text)

                full_assistant_text = "".join(assistant_chunks)

                # Signal end of response with an empty message
                await websocket.send_text("")

                # Append the full assistant response to memory
                session_store.append_message(
                    session_id,
                    ChatMessage(
                        role="assistant",
                        content=full_assistant_text,
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                await websocket.send_text(f"[ERROR] {exc}")
                await websocket.send_text("")

    except WebSocketDisconnect:
        # Normal disconnect
        return
    except Exception as exc:  # noqa: BLE001
        # Unexpected server-side error
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR,
            reason="Internal server error.",
        )
        raise exc

