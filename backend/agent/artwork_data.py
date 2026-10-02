import json
import os
from typing import Any, Dict, List, Optional

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "data_david.json"
)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BACKEND_DIR, "static")
LOCAL_IMAGE_DIR = os.path.join(STATIC_DIR, "artChat_demo")
S3_BASE = "https://seeterature.s3.amazonaws.com/photo/david/"


def _load() -> List[Dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_artwork(artwork_id: str) -> Optional[Dict[str, Any]]:
    for entry in _load():
        if entry.get("eng_id") == artwork_id or entry.get("id") == artwork_id:
            meta = entry.get("meta", {})
            eng_id = entry.get("eng_id", "")
            local_image_path = os.path.join(LOCAL_IMAGE_DIR, eng_id)
            return {
                "artwork_id": eng_id,
                "title": meta.get("title", "N/A"),
                "artist": meta.get("artist", "N/A"),
                "style": meta.get("style", "N/A"),
                "description": entry.get("description", ""),
                "comment": entry.get("comment", ""),
                "explanation": entry.get("explanation", ""),
                "image_path": local_image_path if os.path.exists(local_image_path) else "",
                "image_url": S3_BASE + eng_id,
            }
    return None


def list_artworks() -> List[Dict[str, str]]:
    return [
        {"artwork_id": e.get("eng_id"), "title": e.get("meta", {}).get("title", "N/A")}
        for e in _load()
    ]
