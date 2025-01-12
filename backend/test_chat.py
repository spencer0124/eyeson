import asyncio
from datetime import datetime, date, timedelta, timezone
from routers.chat_router import manager

async def test_write_messages():
    # 1. 가짜 메시지 데이터 추가
    museum_name = "test_museum"
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

    # 2. 로그 파일에 기록 (어제 날짜로 메시지 이동)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    manager.message_history[museum_name] = {yesterday: [fake_message]}  # 강제로 어제 날짜로 이동

    # 3. 파일 저장 함수 호출
    await manager.write_messages_to_files()

# AsyncIO 루프 실행
if __name__ == "__main__":
    asyncio.run(test_write_messages())
