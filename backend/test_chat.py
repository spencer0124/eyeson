# test_chat_router.py
import asyncio
from routers.chat_router import manager

async def test_write_messages():
    # 1. 가짜 메시지 데이터 추가
    museum_name = "test_museum"  # 테스트용 박물관 이름
    fake_message = {
        "type": "message",
        "content": "테스트 메시지입니다.",
        "username": "익명1",
        "museum": museum_name,
        "timestamp": "2025-01-12T10:00:00Z",
        "active_users": ["익명1"]
    }

    # ConnectionManager의 message_history에 메시지 추가
    await manager.add_message_to_history(museum_name, fake_message)

    # 2. 파일 저장 함수 호출 (직접 실행)
    await manager.write_messages_to_files()

# AsyncIO 루프 실행
if __name__ == "__main__":
    asyncio.run(test_write_messages())
