from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, date, timedelta
import redis
import json
import os

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_info: Dict[WebSocket, tuple] = {}
        self.username_counters: Dict[str, int] = {}
        self.user_id_map: Dict[str, str] = {}
        self.last_seen: Dict[str, datetime] = {}
        self.lock = asyncio.Lock()

        # Redis 클라이언트 초기화
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

        # 스케줄러 설정
        self.cleanup_interval = timedelta(hours=24)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.archive_and_clear_old_messages, 'cron', hour=0, minute=0)  # 매일 자정 실행

        os.makedirs("logs", exist_ok=True)

    def start_scheduler(self):
        self.scheduler.start()
        
    def generate_unique_key(self, websocket: WebSocket, museum: str) -> str:
        """유저를 고유하게 식별하기 위한 키 생성"""
        client_ip = websocket.client.host  # 유저의 IP 주소
        user_agent = websocket.headers.get("user-agent", "unknown")
        return f"{museum}-{client_ip}-{user_agent}"

    def generate_username(self, museum: str, unique_key: str, artworkid: str) -> str:
        """익명 ID를 생성하거나 기존 ID를 반환 (artworkid 포함)"""
        if unique_key not in self.user_id_map:
            if museum not in self.username_counters:
                self.username_counters[museum] = 1
            username_number = self.username_counters[museum]
            self.username_counters[museum] += 1
            self.user_id_map[unique_key] = f"관람객{username_number}"
        return f"{self.user_id_map[unique_key]} ({artworkid})"

    async def connect(self, websocket: WebSocket, museum: str):
        """유저 연결 처리"""
        origin = websocket.headers.get('origin')
        allowed_origins = ["http://43.201.93.53:8000"]
        if "*" not in allowed_origins and origin not in allowed_origins:
            await websocket.close(code=1008, reason="CORS policy violation")
            return
        await websocket.accept()

        if museum not in self.active_connections:
            self.active_connections[museum] = []
        self.active_connections[museum].append(websocket)

        artworkid = websocket.query_params.get('artworkid', 'unknown')
        unique_key = self.generate_unique_key(websocket, museum)
        username = self.generate_username(museum, unique_key, artworkid)

        # 마지막 접속 시간 갱신 (Redis에 저장)
        await self.update_last_seen(unique_key)

        # 유저 정보 저장
        self.user_info[websocket] = (museum, username, artworkid)

        # 저장된 오늘의 메시지 전송
        today_messages = await self.get_messages_for_museum(museum)
        for message in today_messages:
            await websocket.send_json(message)

        # 입장 메시지 전송
        system_message = self.format_message(
            message_type="system",
            content=f"{username}이 채팅방에 들어왔습니다.",
            username="System",
            museum=museum,
            active_users=self.get_active_users(museum)
        )
        await self.broadcast(museum, system_message)

    async def disconnect(self, websocket: WebSocket):
        """유저가 채팅방을 떠날 때 호출"""
        if websocket in self.user_info:
            museum, username, artworkid = self.user_info[websocket]
            self.active_connections[museum].remove(websocket)
            if not self.active_connections[museum]:
                del self.active_connections[museum]
            del self.user_info[websocket]

            # 퇴장 메시지 전송
            system_message = self.format_message(
                message_type="system",
                content=f"{username}이 채팅방을 나갔습니다.",
                username="System",
                museum=museum,
                active_users=self.get_active_users(museum)
            )
            await self.broadcast(museum, system_message)

    async def broadcast(self, museum: str, message: dict):
        """특정 박물관 채팅방의 모든 사용자에게 메시지 전송"""
        if museum in self.active_connections:
            for connection in self.active_connections[museum]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message to {self.user_info[connection][1]}: {e}")

    def format_message(
        self, message_type: str, content: str, username: str, museum: str, active_users: List[str]
    ) -> Dict[str, str]:
        """채팅 메시지 포맷 통일"""
        return {
            "type": message_type,
            "content": content,
            "username": username,
            "museum": museum,
            "timestamp": datetime.now().isoformat(),
            "active_users": active_users
        }

    async def save_message_to_redis(self, museum: str, message: dict):
        """Redis에 메시지를 저장"""
        today_str = date.today().isoformat()
        redis_key = f"chat:{museum}:{today_str}"
        self.redis_client.rpush(redis_key, json.dumps(message))

    async def get_messages_for_museum(self, museum: str):
        """Redis에서 특정 박물관의 오늘 메시지 가져오기"""
        today_str = date.today().isoformat()
        redis_key = f"chat:{museum}:{today_str}"
        messages = self.redis_client.lrange(redis_key, 0, -1)
        return [json.loads(message) for message in messages]

    async def archive_and_clear_old_messages(self):
        """하루가 지나면 Redis 데이터를 로그 파일로 저장하고 삭제"""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        redis_keys = self.redis_client.keys(f"chat:*:{yesterday}")

        for redis_key in redis_keys:
            museum = redis_key.split(":")[1]
            messages = self.redis_client.lrange(redis_key, 0, -1)

            # 로그 파일에 저장 후 redis에서 삭제
            log_filename = f"logs/museum{museum}_{yesterday}.log"
            with open(log_filename, "a", encoding="utf-8") as f:
                for message in messages:
                    f.write(message + "\n")
            self.redis_client.delete(redis_key)

    async def update_last_seen(self, unique_key: str):
        """Redis에 유저의 마지막 접속 시간 업데이트"""
        now = datetime.now().isoformat()
        redis_key = f"user:last_seen:{unique_key}"
        
        # Redis에 유저의 마지막 접속 시간 저장 및 TTL 설정 (24시간)
        self.redis_client.set(redis_key, now, ex=24 * 60 * 60)
        print(f"Updated last_seen for {unique_key} at {now}")

    async def cleanup_old_users(self):
        """오래된 유저 정보를 Redis에서 정리"""
        # Redis에 저장된 모든 last_seen 키 가져오기
        keys = self.redis_client.keys("user:last_seen:*")
        now = datetime.now()

        cleaned_count = 0
        for key in keys:
            # Redis에서 마지막 접속 시간 불러오기
            last_seen = self.redis_client.get(key)
            if last_seen:
                last_seen_time = datetime.fromisoformat(last_seen)
                if now - last_seen_time > timedelta(hours=24):
                    # 24시간 이상 지난 유저를 Redis에서 제거
                    self.redis_client.delete(key)
                    cleaned_count += 1

        print(f"Cleaned up {cleaned_count} old users.")

    async def shutdown(self):
        """ConnectionManager 종료 시 호출되어야 하는 함수"""
        print("Shutting down ConnectionManager...")
        self.scheduler.shutdown(wait=False)  # 스케줄러 종료
        if hasattr(self, 'cleanup_task') and self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

manager = ConnectionManager()

@router.websocket("/ws/{museum}")
async def websocket_endpoint(websocket: WebSocket, museum: str):
    try:
        await manager.connect(websocket, museum)
        while True:
            data = await websocket.receive_text()
            message = manager.format_message(
                message_type="message",
                content=data,
                username=manager.user_info[websocket][1],  # 유저 이름
                museum=museum,
                active_users=manager.get_active_users(museum)
            )
            await manager.save_message_to_redis(museum, message)  # Redis에 메시지 저장
            await manager.broadcast(museum, message)  # 메시지 브로드캐스트

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"Unexpected error: {e}")
        await websocket.close(code=1008, reason="Internal server error")