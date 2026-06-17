from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from app.schemas.roleplay import (
    RolePlaySessionCreateRequest,
    RolePlaySessionCreateResponse,
    RolePlayPerformRequest,
    RolePlayContinueRequest,
    RolePlayChangeSceneRequest,
)
from app.services.roleplay_service import RolePlayService


router = APIRouter(
    prefix="/v1/eburon/talkhuman/roleplay",
    tags=["Eburon AI TalkHuman RolePlay"]
)


@router.post("/sessions", response_model=RolePlaySessionCreateResponse)
async def create_roleplay_session(payload: RolePlaySessionCreateRequest):
    try:
        session = await RolePlayService.create_session(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "provider": "Eburon AI",
                "product": "TalkHuman",
                "feature": "RolePlay",
                "model": "talkhuman-3.1",
                "error": {
                    "code": "EBURON_TALKHUMAN_VOICE_NOT_FOUND",
                    "message": "The requested Eburon AI voice alias was not found.",
                },
            },
        ) from exc

    return {
        "provider": "Eburon AI",
        "product": "TalkHuman",
        "feature": "RolePlay",
        "model": payload.model,
        "voice_name": session["voice_name"],
        "session_id": session["session_id"],
        "status": session["status"],
        "created_at": session["created_at"],
    }


@router.get("/sessions/{session_id}")
async def get_roleplay_session(session_id: str):
    session = await RolePlayService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        "provider": "Eburon AI",
        "product": "TalkHuman",
        "feature": "RolePlay",
        "model": "talkhuman-3.1",
        "voice_name": session.get("voice_name", "Batman"),
        "session_id": session_id,
        "status": session["status"],
    }


@router.delete("/sessions/{session_id}")
async def delete_roleplay_session(session_id: str):
    success = await RolePlayService.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        "provider": "Eburon AI",
        "product": "TalkHuman",
        "feature": "RolePlay",
        "model": "talkhuman-3.1",
        "session_id": session_id,
        "status": "deleted",
    }


@router.post("/sessions/{session_id}/perform")
async def perform_roleplay(session_id: str, payload: RolePlayPerformRequest):
    response = await RolePlayService.perform(session_id, payload)
    if not response:
        raise HTTPException(status_code=404, detail="Session not found")

    return response


@router.post("/sessions/{session_id}/continue")
async def continue_roleplay(session_id: str, payload: RolePlayContinueRequest):
    session = await RolePlayService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        "provider": "Eburon AI",
        "product": "TalkHuman",
        "feature": "RolePlay",
        "model": "talkhuman-3.1",
        "session_id": session_id,
        "status": "continuing",
    }


@router.post("/sessions/{session_id}/interrupt")
async def interrupt_roleplay(session_id: str):
    session = await RolePlayService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        "provider": "Eburon AI",
        "product": "TalkHuman",
        "feature": "RolePlay",
        "model": "talkhuman-3.1",
        "session_id": session_id,
        "status": "interrupted",
    }


@router.post("/sessions/{session_id}/change-scene")
async def change_roleplay_scene(
    session_id: str,
    payload: RolePlayChangeSceneRequest,
):
    session = await RolePlayService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session["active_scene"] = payload.new_topic_or_roleplay_request
    
    return {
        "provider": "Eburon AI",
        "product": "TalkHuman",
        "feature": "RolePlay",
        "model": "talkhuman-3.1",
        "session_id": session_id,
        "status": "scene_changed",
        "transition_style": payload.transition_style,
    }


@router.websocket("/ws")
async def roleplay_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        await websocket.send_json({
            "type": "status",
            "provider": "Eburon AI",
            "product": "TalkHuman",
            "feature": "RolePlay",
            "model": "talkhuman-3.1",
            "status": "connected"
        })

        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if msg_type == "start_roleplay":
                await websocket.send_json({
                    "type": "status",
                    "provider": "Eburon AI",
                    "model": "talkhuman-3.1",
                    "feature": "RolePlay",
                    "status": "performing"
                })
                
                # Simulate a few events for the playground
                await websocket.send_json({
                    "type": "roleplay_text",
                    "provider": "Eburon AI",
                    "product": "TalkHuman",
                    "feature": "RolePlay",
                    "model": "talkhuman-3.1",
                    "text": "[clears throat] The signal... it's fading. If anyone can hear this..."
                })
                
                await websocket.send_json({
                    "type": "roleplay_expression",
                    "provider": "Eburon AI",
                    "product": "TalkHuman",
                    "feature": "RolePlay",
                    "model": "talkhuman-3.1",
                    "expression": "voice_lowers",
                    "emotion": "melancholy",
                    "intensity": 0.8
                })

            elif msg_type == "continue":
                await websocket.send_json({
                    "type": "status",
                    "provider": "Eburon AI",
                    "model": "talkhuman-3.1",
                    "feature": "RolePlay",
                    "status": "continuing"
                })

            elif msg_type == "interrupt":
                await websocket.send_json({
                    "type": "status",
                    "provider": "Eburon AI",
                    "model": "talkhuman-3.1",
                    "feature": "RolePlay",
                    "status": "interrupted"
                })

            elif msg_type == "change_scene":
                await websocket.send_json({
                    "type": "status",
                    "provider": "Eburon AI",
                    "model": "talkhuman-3.1",
                    "feature": "RolePlay",
                    "status": "scene_changed"
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "provider": "Eburon AI",
                    "model": "talkhuman-3.1",
                    "feature": "RolePlay",
                    "error": {
                        "code": "UNKNOWN_ROLEPLAY_MESSAGE",
                        "message": "Unsupported RolePlay WebSocket message type."
                    }
                })

    except WebSocketDisconnect:
        # TODO:
        # - Cleanup session if this socket owns it.
        pass
