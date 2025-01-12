from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
from datetime import datetime, date, timedelta, timezone
import asyncio
from starlette.websockets import WebSocketState
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import json

router = APIRouter()

# ConnectionManager 클래스
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_info: Dict[WebSocket, tuple] = {}  # (museum, username, artworkid)
        self.username_counters: Dict[str, int] = {}  # 박물관별 유저 이름 카운터
        self.message_history: Dict[str, Dict[str, List[dict]]] = {}  # 박물관별, 날짜별 메시지 기록
        self.user_id_map: Dict[str, str] = {}  # 고유 식별자 -> 익명 ID 매핑
        self.last_seen: Dict[str, datetime] = {}  # 고유 식별자 -> 마지막 접속 시간
        self.lock = asyncio.Lock()  # 동시성 보호를 위한 락
        self.cleanup_interval = timedelta(hours=24)  # 정리 간격 (24시간)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.write_messages_to_files, 'cron', hour=0, minute=0)  # 매일 자정 메시지 기록 저장
        self.scheduler.add_job(self.cleanup_old_users, 'interval', hours=1)  # 매시간 오래된 유저 정리
        self.scheduler.start()
        os.makedirs("logs", exist_ok=True)

    def generate_unique_key(self, websocket: WebSocket, museum: str) -> str:
        """유저를 고유하게 식별하기 위한 키 생성"""
        client_ip = websocket.client.host  # 유저의 IP 주소
        user_agent = websocket.headers.get("user-agent", "unknown")
        return f"{museum}-{client_ip}-{user_agent}"

    def generate_username(self, museum: str, unique_key: str) -> str:
        """익명 ID를 생성하거나 기존 ID를 반환"""
        if unique_key not in self.user_id_map:
            # 익명 ID 생성
            if museum not in self.username_counters:
                self.username_counters[museum] = 1
            username_number = self.username_counters[museum]
            self.username_counters[museum] += 1
            self.user_id_map[unique_key] = f"익명{username_number}"
        return self.user_id_map[unique_key]

    async def connect(self, websocket: WebSocket, museum: str):
        """유저 연결 처리"""
        origin = websocket.headers.get('origin')
        print(f"WebSocket origin: {origin}")
        allowed_origins = ["http://43.201.93.53:8000"]
        if "*" not in allowed_origins and origin not in allowed_origins:
            await websocket.close(code=1008, reason="CORS policy violation")
            return

        await websocket.accept()

        if museum not in self.active_connections:
            self.active_connections[museum] = []

        self.active_connections[museum].append(websocket)

        # Get artworkid from query params
        artworkid = websocket.query_params.get('artworkid', 'unknown')

        # 고유 키 생성 및 익명 ID 가져오기
        unique_key = self.generate_unique_key(websocket, museum)
        username = self.generate_username(museum, unique_key)

        # 마지막 접속 시간 갱신
        self.last_seen[unique_key] = datetime.now(timezone.utc)

        # 유저 정보 저장
        self.user_info[websocket] = (museum, username, artworkid)

        # 저장된 오늘의 메시지 전송
        await self.send_history(websocket, museum)

        # 입장 메시지 전송
        system_message = self.format_message(
            message_type="system",
            content=f"{username} joined the museum chat",
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
                content=f"{username} left the museum chat",
                username="System",
                museum=museum,
                active_users=self.get_active_users(museum)
            )
            await self.broadcast(museum, system_message)

    async def cleanup_old_users(self):
        """오래된 유저 정보를 정리"""
        now = datetime.now(timezone.utc)
        async with self.lock:
            keys_to_remove = []
            for unique_key, last_seen_time in self.last_seen.items():
                if now - last_seen_time > self.cleanup_interval:
                    # 마지막 접속 시간 기준으로 오래된 유저 식별
                    keys_to_remove.append(unique_key)
            
            # 오래된 유저 정보 삭제
            for key in keys_to_remove:
                if key in self.user_id_map:
                    del self.user_id_map[key]
                if key in self.last_seen:
                    del self.last_seen[key]
            
            print(f"Cleaned up {len(keys_to_remove)} old users.")

    async def broadcast(self, museum: str, message: dict):
        """특정 박물관 채팅방의 모든 사용자에게 메시지 전송"""
        if museum in self.active_connections:
            for connection in self.active_connections[museum]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message to {self.user_info[connection][1]}: {e}")
                    
    def get_active_users(self, museum: str) -> List[str]:
        """특정 박물관 채팅방의 현재 접속자 목록"""
        if museum not in self.active_connections:
            return []
        return [self.user_info[ws][1] for ws in self.active_connections[museum]]

    def get_active_museums(self) -> List[str]:
        """현재 활성화된 박물관 채팅방 목록"""
        return list(self.active_connections.keys())

    def format_message(
        self, message_type: str, content: str, username: str, museum: str, active_users: List[str]
    ) -> Dict[str, str]:
        """채팅 메시지 포맷 통일"""
        return {
            "type": message_type,
            "content": content,
            "username": username,
            "museum": museum,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_users": active_users
        }

    async def add_message_to_history(self, museum: str, message: dict):
        """메시지를 저장소에 추가"""
        today_str = date.today().isoformat()
        async with self.lock:
            if museum not in self.message_history:
                self.message_history[museum] = {}
            if today_str not in self.message_history[museum]:
                self.message_history[museum][today_str] = []
            self.message_history[museum][today_str].append(message)

    async def send_history(self, websocket: WebSocket, museum: str):
        """접속하는 유저에게 오늘의 메시지 히스토리 전송"""
        today_str = date.today().isoformat()
        async with self.lock:
            today_messages = self.message_history.get(museum, {}).get(today_str, [])
        for message in today_messages:
            await websocket.send_json(message)

    async def write_messages_to_files(self):
        """하루가 끝날 때마다 각 박물관별 메시지 히스토리를 파일로 저장"""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        async with self.lock:
            for museum, dates in self.message_history.items():
                if yesterday in dates:
                    messages = dates[yesterday]
                    log_filename = f"logs/museum_{museum}_{yesterday}.log"
                    try:
                        with open(log_filename, "a", encoding="utf-8") as f:
                            for message in messages:
                                f.write(json.dumps(message, ensure_ascii=False) + "\n")
                        print(f"Saved {len(messages)} messages for museum {museum} to {log_filename}")
                    except Exception as e:
                        print(f"Error writing messages to file for museum {museum}: {e}")
                    # 메시지 기록 삭제
                    del dates[yesterday]

    async def shutdown(self):
        """ConnectionManager 종료 시 호출되어야 하는 함수"""
        self.scheduler.shutdown(wait=False)
        self.cleanup_task.cancel()
        try:
            await self.cleanup_task
        except asyncio.CancelledError:
            pass

manager = ConnectionManager()

@router.websocket("/ws/{museum}")
async def websocket_endpoint(websocket: WebSocket, museum: str):
    print("WebSocket endpoint called")  # 추가된 로그
    try:
        await manager.connect(websocket, museum)
        # 연결이 거부된 경우, WebSocket의 상태가 CONNECTED가 아님
        if websocket.application_state != WebSocketState.CONNECTED:
            return  # 연결이 거부된 경우 더 이상 진행하지 않음

        while True:
            data = await websocket.receive_text()
            message = manager.format_message(
                message_type="message",
                content=data,
                username=manager.user_info[websocket][1],  # 유저 이름 (이미 artworkid 포함)
                museum=museum,
                active_users=manager.get_active_users(museum)
            )
            await manager.add_message_to_history(museum, message)  # 메시지 저장
            await manager.broadcast(museum, message)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"Unexpected error: {e}")
        await websocket.close(code=1008, reason="Internal server error")  # 유효한 코드로 변경

@router.get("/museums")
async def get_active_museums():
    museums = manager.get_active_museums()
    return {
        "museums": museums,
        "total": len(museums)
    }

@router.get("/museums/{museum}/users")
async def get_museum_users(museum: str):
    users = manager.get_active_users(museum)
    return {
        "museum": museum,
        "users": users,
        "total": len(users)
    }