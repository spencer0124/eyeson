import json
import os
from datetime import datetime
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import BaseModel

from agent.art_agent_lc import ArtAgentLC

router = APIRouter()

KST = ZoneInfo("Asia/Seoul")
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BACKEND_DIR, "logs")


class AgentRequest(BaseModel):
    user_id: str = "local_demo_user"
    artwork_id: str = "wanderer-above-the-sea-of-fog.jpg"
    model: str = "gpt-4o"


class AgentChatRequest(AgentRequest):
    message: str


def _agent(req: AgentRequest) -> ArtAgentLC:
    return ArtAgentLC(
        user_id=req.user_id,
        artwork_id=req.artwork_id,
        model=req.model,
        thread_id=f"{req.user_id}:{req.artwork_id}",
    )


def _message_to_dict(message: Any) -> Dict[str, str]:
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    elif isinstance(message, ToolMessage):
        role = "tool"
    else:
        role = getattr(message, "type", "message")

    content = message.content if isinstance(message.content, str) else str(message.content)
    return {"role": role, "content": content}


def _visible_messages(messages: List[Any]) -> List[Dict[str, str]]:
    visible = []
    for message in messages:
        item = _message_to_dict(message)
        if not item["content"].strip():
            continue
        if item["role"] == "user" and item["content"].startswith("(system trigger:"):
            continue
        if item["role"] == "tool":
            continue
        visible.append(item)
    return visible


def _log_path() -> str:
    day = datetime.now(KST).date().isoformat()
    return os.path.join(LOG_DIR, f"agent_chat_{day}.jsonl")


def _write_agent_log(event: str, payload: Dict[str, Any]) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    record = {
        "timestamp": datetime.now(KST).isoformat(),
        "event": event,
        **payload,
    }
    with open(_log_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@router.post("/start")
async def start_agent(req: AgentRequest):
    try:
        agent = _agent(req)
        resumed = agent.has_checkpoint()
        reply = agent.start_conversation()
        messages = _visible_messages(agent.checkpoint_messages())
        response = {
            "reply": reply,
            "resumed": resumed,
            "thread_id": agent.thread_id,
            "messages": messages,
        }
        _write_agent_log(
            "start",
            {
                "user_id": req.user_id,
                "artwork_id": req.artwork_id,
                "model": req.model,
                "thread_id": agent.thread_id,
                "resumed": resumed,
                "reply": reply,
                "messages": messages,
            },
        )
        return response
    except Exception as e:
        _write_agent_log(
            "start_error",
            {
                "user_id": req.user_id,
                "artwork_id": req.artwork_id,
                "model": req.model,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_agent(req: AgentChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    try:
        agent = _agent(req)
        reply = agent.chat(req.message)
        messages = _visible_messages(agent.checkpoint_messages())
        response = {
            "reply": reply,
            "thread_id": agent.thread_id,
            "messages": messages,
        }
        _write_agent_log(
            "chat",
            {
                "user_id": req.user_id,
                "artwork_id": req.artwork_id,
                "model": req.model,
                "thread_id": agent.thread_id,
                "message": req.message,
                "reply": reply,
                "messages": messages,
            },
        )
        return response
    except Exception as e:
        _write_agent_log(
            "chat_error",
            {
                "user_id": req.user_id,
                "artwork_id": req.artwork_id,
                "model": req.model,
                "message": req.message,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def agent_history(user_id: str = "local_demo_user", artwork_id: str = "wanderer-above-the-sea-of-fog.jpg"):
    try:
        req = AgentRequest(user_id=user_id, artwork_id=artwork_id)
        agent = _agent(req)
        return {
            "thread_id": agent.thread_id,
            "messages": _visible_messages(agent.checkpoint_messages()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/log-path")
async def agent_log_path():
    return {"log_path": _log_path()}
