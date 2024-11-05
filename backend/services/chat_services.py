from datetime import datetime
from typing import Dict, Any, List

def format_message(
    message_type: str,
    content: str,
    username: str,
    museum: str,
    active_users: List[str]
) -> Dict[str, Any]:
    """채팅 메시지 포맷 통일"""
    return {
        "type": message_type,
        "content": content,
        "username": username,
        "museum": museum,
        "timestamp": datetime.now().isoformat(),
        "active_users": active_users
    }

def validate_username(username: str) -> bool:
    """사용자 이름 유효성 검사
    - 2-20자 길이
    - 공백 불가
    """
    if not username or len(username) < 2 or len(username) > 20:
        return False
    if ' ' in username:
        return False
    return True

def validate_museum_name(museum: str) -> bool:
    """박물관 이름 유효성 검사
    - 2-50자 길이
    - 알파벳, 숫자, 공백, 하이픈만 허용
    """
    if not museum or len(museum) < 2 or len(museum) > 50:
        return False
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- ")
    if not all(char in valid_chars for char in museum):
        return False
    return True