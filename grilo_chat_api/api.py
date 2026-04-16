"""
FastAPI endpoints for Unified Chat API.

Provides REST endpoints for:
- POST /chat/message - Send a message
- GET /chat/sessions - List sessions
- GET /chat/sessions/{id} - Get session details
- POST /chat/sessions - Create new session
- GET /chat/plugins - List available plugins
- POST /chat/escalate - Trigger escalation

Usage:
    uvicorn grilo_chat_api.api:app --reload
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from grilo_chat_api import ChatAPIService, GlobalChatAPI

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Grilo Falante Chat API",
    description="Unified Chat API for domain plugins",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    """Request to send a chat message."""
    query: str
    user_id: str
    session_id: Optional[str] = None
    domain_hint: Optional[str] = None
    llm_provider: Optional[str] = "bitnet"


class SessionCreateRequest(BaseModel):
    """Request to create a new session."""
    user_id: str
    domain: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class EscalateRequest(BaseModel):
    """Request to trigger escalation."""
    session_id: str
    reason: Optional[str] = None
    operator_id: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "grilo-chat-api"}


@app.get("/plugins")
async def list_plugins():
    """List all available domain plugins."""
    from grilo_falante.platform import PluginRegistry

    plugins = []
    for name in PluginRegistry.list_plugins():
        try:
            adapter = PluginRegistry.get(name)
            meta = adapter.get_metadata()
            plugins.append({
                "name": meta.name,
                "version": meta.version,
                "description": meta.description,
                "status": meta.status.value,
                "routing_keywords": adapter.get_routing_config(),
                "escalation_triggers": adapter.get_escalation_triggers(),
            })
        except Exception as e:
            logger.warning(f"Could not load plugin {name}: {e}")

    return {"plugins": plugins, "count": len(plugins)}


@app.post("/chat/message")
async def send_message(request: MessageRequest):
    """
    Send a chat message and get a response.

    This is the main endpoint for chatting with domain plugins.
    Automatically routes to the appropriate plugin based on query content.
    """
    api = GlobalChatAPI.get_instance()

    llm_config = {"provider": request.llm_provider or "bitnet"}

    try:
        result = await api.process_message(
            query=request.query,
            user_id=request.user_id,
            session_id=request.session_id,
            domain_hint=request.domain_hint,
            llm_config=llm_config,
        )

        return result

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/sessions")
async def list_sessions(user_id: Optional[str] = None):
    """List all chat sessions, optionally filtered by user."""
    api = GlobalChatAPI.get_instance()
    return {"sessions": api.list_sessions(user_id=user_id)}


@app.get("/chat/sessions/{session_id}")
async def get_session(session_id: str):
    """Get details of a specific session."""
    api = GlobalChatAPI.get_instance()
    session = api.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "messages": session.messages,
        "active_domain": session.active_domain,
        "escalation_active": session.escalation_active,
        "context": session.context,
    }


@app.post("/chat/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new chat session."""
    api = GlobalChatAPI.get_instance()
    session = api.create_session(
        user_id=request.user_id,
        domain=request.domain,
        context=request.context,
    )

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "created_at": session.created_at.isoformat(),
        "active_domain": session.active_domain,
    }


@app.post("/chat/escalate")
async def trigger_escalation(request: EscalateRequest):
    """
    Manually trigger escalation for a session.

    This allows an operator to take over a conversation.
    """
    api = GlobalChatAPI.get_instance()
    session = api.get_session(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.escalation_active = True

    api.add_message(
        session_id=session.session_id,
        role="system",
        content=f"Escalation triggered: {request.reason or 'Manual escalation'}",
        metadata={"operator_id": request.operator_id, "type": "escalation"},
    )

    return {
        "success": True,
        "session_id": session.session_id,
        "escalation_active": True,
    }


@app.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
):
    """Get chat history for a session with pagination."""
    api = GlobalChatAPI.get_instance()
    session = api.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = session.messages[offset : offset + limit]

    return {
        "session_id": session_id,
        "messages": messages,
        "total": len(session.messages),
        "limit": limit,
        "offset": offset,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
