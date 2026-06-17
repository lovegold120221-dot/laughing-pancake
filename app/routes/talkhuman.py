# app/routes/talkhuman.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.schemas.talkhuman import (
    TalkHumanSessionCreateRequest,
    TalkHumanSessionCreateResponse,
    TalkHumanMessageRequest,
)
from app.core.talkhuman_voices import list_public_talkhuman_voices
from app.services.talkhuman_service import TalkHumanService

router = APIRouter(
    prefix="/v1/eburon/talkhuman",
    tags=["Eburon AI TalkHuman"]
)


@router.get("/voices")
async def list_talkhuman_voices():
    voices = list_public_talkhuman_voices()
    return {
        "provider": "Eburon AI",
        "product": "TalkHuman",
        "model": "talkhuman-3.1",
        "voices": voices,
        "count": len(voices),
    }


@router.post("/sessions", response_model=TalkHumanSessionCreateResponse)
async def create_talkhuman_session(payload: TalkHumanSessionCreateRequest):
    try:
        session = await TalkHumanService.create_session(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "provider": "Eburon AI",
                "product": "TalkHuman",
                "model": "talkhuman-3.1",
                "error": {
                    "code": "EBURON_TALKHUMAN_VOICE_NOT_FOUND",
                    "message": "The requested Eburon AI voice alias was not found.",
                },
            },
        ) from exc
    
    return {
        "session_id": session["session_id"],
        "provider": "Eburon AI",
        "model": payload.model,
        "product": "TalkHuman",
        "voice_name": session["voice_alias"],
        "status": session["status"],
        "created_at": session["created_at"],
    }


@router.get("/sessions/{session_id}")
async def get_talkhuman_session(session_id: str):
    session = await TalkHumanService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session["session_id"],
        "provider": "Eburon AI",
        "model": "talkhuman-3.1",
        "voice_name": session.get("voice_alias", "Phoenix"),
        "status": session["status"],
        "created_at": session["created_at"]
    }


@router.delete("/sessions/{session_id}")
async def delete_talkhuman_session(session_id: str):
    success = await TalkHumanService.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "deleted", "session_id": session_id}


@router.post("/sessions/{session_id}/message")
async def send_talkhuman_message(
    session_id: str,
    payload: TalkHumanMessageRequest,
):
    response = await TalkHumanService.process_message(session_id, payload)
    if not response:
        raise HTTPException(status_code=404, detail="Session not found")

    return response


@router.websocket("/ws")
async def talkhuman_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_json()
            # Simple WS loop for simulation
            await websocket.send_json({
                "type": "status",
                "provider": "Eburon AI",
                "model": "talkhuman-3.1",
                "status": "received",
                "echo": message
            })

    except WebSocketDisconnect:
        pass
