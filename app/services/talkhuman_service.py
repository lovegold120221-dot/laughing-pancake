import asyncio
import os
import uuid
from datetime import datetime, UTC
from typing import Dict, Optional

from app.core.model_aliases import resolve_public_model
from app.core.talkhuman_prompt import build_talkhuman_instruction
from app.core.talkhuman_voices import resolve_talkhuman_voice

# Simple in-memory session store
# In a production app, this would use Redis or a database
sessions: Dict[str, dict] = {}

class TalkHumanService:
    @staticmethod
    async def create_session(payload):
        session_id = f"th_{uuid.uuid4().hex[:12]}"
        
        # Resolve internal model
        internal_model = resolve_public_model(payload.model)
        voice = resolve_talkhuman_voice(payload.voice_name)
        
        # Build the initial humanized instruction
        instruction = build_talkhuman_instruction(
            personality=payload.personality,
            system_behavior=payload.system_behavior
        )
        
        # Store session state
        sessions[session_id] = {
            "session_id": session_id,
            "internal_model": internal_model,
            "internal_voice": voice["private_voice"],
            "voice_alias": voice["alias"],
            "personality": payload.personality,
            "instruction": instruction,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "created",
            "history": [],
            "voice_profile": payload.voice_profile.model_dump() if hasattr(payload.voice_profile, "model_dump") else payload.voice_profile
        }
        
        return sessions[session_id]

    @staticmethod
    async def get_session(session_id: str):
        return sessions.get(session_id)

    @staticmethod
    async def delete_session(session_id: str):
        if session_id in sessions:
            del sessions[session_id]
            return True
        return False

    @staticmethod
    async def process_message(session_id: str, payload):
        session = sessions.get(session_id)
        if not session:
            return None
            
        # Update instruction based on current emotional intent/expression hint
        session["instruction"] = build_talkhuman_instruction(
            personality=session["personality"],
            emotional_intent=payload.emotional_intent,
            expression_hint=payload.expression_hint
        )
        
        # Simulate interaction with internal model
        # In a real implementation, this would call the Gemini Live SDK
        # For this "make it work" phase, we'll simulate a natural response
        
        response_text = f"As Eburon AI, I hear you. [Emotional: {payload.emotional_intent}] You said: {payload.text}"
        
        if payload.expression_hint == "laugh":
            response_text = "Haha! " + response_text
        elif payload.expression_hint == "sigh":
            response_text = "(Sighs softly) " + response_text

        session["history"].append({"role": "user", "content": payload.text})
        session["history"].append({"role": "assistant", "content": response_text})
        
        return {
            "provider": "Eburon AI",
            "model": "talkhuman-3.1",
            "session_id": session_id,
            "voice_name": session["voice_alias"],
            "status": "sent",
            "emotional_intent": payload.emotional_intent,
            "expression_hint": payload.expression_hint,
            "response": response_text
        }
