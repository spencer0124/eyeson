import json
import os
import time
from typing import Any, Dict

PERSONA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "personas")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _path(user_id: str) -> str:
    safe_id = "".join(c for c in user_id if c.isalnum() or c in ("-", "_")) or "default"
    return os.path.join(PERSONA_DIR, f"{safe_id}.json")


def load_persona(user_id: str) -> Dict[str, Any]:
    path = _path(user_id)
    if not os.path.exists(path):
        return {"user_id": user_id, "preferences": {}, "created_at": _now(), "updated_at": _now()}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_persona(persona: Dict[str, Any]) -> None:
    os.makedirs(PERSONA_DIR, exist_ok=True)
    persona["updated_at"] = _now()
    with open(_path(persona["user_id"]), "w", encoding="utf-8") as f:
        json.dump(persona, f, ensure_ascii=False, indent=2)


def upsert_preference(user_id: str, key: str, value: str, source: str = "inferred", reason: str = "") -> Dict[str, Any]:
    persona = load_persona(user_id)
    prefs = persona.setdefault("preferences", {})
    existing = prefs.get(key)
    evidence_count = (existing["evidence_count"] + 1) if existing else 1
    prefs[key] = {
        "value": value,
        "source": source,
        "reason": reason,
        "evidence_count": evidence_count,
        "updated_at": _now(),
    }
    save_persona(persona)
    return persona


def persona_summary_text(user_id: str) -> str:
    persona = load_persona(user_id)
    prefs = persona.get("preferences", {})
    if not prefs:
        return "(아직 저장된 사용자 선호 없음 - 기본 스타일 사용)"
    lines = []
    for key, info in prefs.items():
        lines.append(f"- {key}: {info['value']} (근거: {info.get('source')}, 언급 {info.get('evidence_count', 1)}회)")
    return "\n".join(lines)
