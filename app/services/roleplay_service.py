import uuid
from datetime import datetime, timezone
from typing import Dict

from app.core.roleplay_prompt import build_roleplay_instruction
from app.core.talkhuman_voices import resolve_talkhuman_voice

# In-memory session store for RolePlay
roleplay_sessions: Dict[str, dict] = {}

class RolePlayService:
    @staticmethod
    async def create_session(payload):
        session_id = f"rp_{uuid.uuid4().hex[:16]}"
        voice = resolve_talkhuman_voice(payload.voice_name)
        
        # Store session state
        roleplay_sessions[session_id] = {
            "session_id": session_id,
            "model": payload.model,
            "voice_name": voice["alias"],
            "internal_voice": voice["private_voice"],
            "roleplay_mode": payload.roleplay_mode,
            "performance_profile": payload.performance_profile.model_dump(),
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active_scene": None,
            "history": []
        }
        
        return roleplay_sessions[session_id]

    @staticmethod
    async def get_session(session_id: str):
        return roleplay_sessions.get(session_id)

    @staticmethod
    async def delete_session(session_id: str):
        if session_id in roleplay_sessions:
            del roleplay_sessions[session_id]
            return True
        return False

    @staticmethod
    async def perform(session_id: str, payload):
        session = roleplay_sessions.get(session_id)
        if not session:
            return None
            
        instruction = build_roleplay_instruction(
            topic_or_roleplay_request=payload.topic_or_roleplay_request,
            tone=payload.tone,
            roleplay_mode=session["roleplay_mode"],
            allow_performance_cues=payload.allow_performance_cues
        )
        
        session["active_scene"] = payload.topic_or_roleplay_request
        session["status"] = "performing"
        
        # In a real app, this would trigger the Gemini Live session with the instruction
        response_text = f"Performing scene: {payload.topic_or_roleplay_request} with tone {payload.tone}."
        
        return {
            "provider": "Eburon AI",
            "product": "TalkHuman",
            "feature": "RolePlay",
            "model": "talkhuman-3.1",
            "session_id": session_id,
            "voice_name": session["voice_name"],
            "status": "performing",
            "tone": payload.tone,
            "response": response_text
        }
