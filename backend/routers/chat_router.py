from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import List, Dict
from datetime import datetime, date
import asyncio
from starlette.websockets import WebSocketState

router = APIRouter()

# ConnectionManager 클래스 (이전 코드 유지)
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_info: Dict[WebSocket, tuple] = {}  # (museum, username, artwork)
        self.username_counters: Dict[str, int] = {}  # 박물관별 유저 이름 카운터
        self.message_history: Dict[str, List[dict]] = {}  # 박물관별 메시지 기록
        self.cleanup_task = asyncio.create_task(self.cleanup_old_messages())  # 백그라운드 작업 시작

    def generate_username(self, museum: str) -> str:
        """박물관별로 유저 이름을 자동으로 생성 ('익명1', '익명2'...)"""
        if museum not in self.username_counters:
            self.username_counters[museum] = 1  # 최초 연결 시 카운터를 1로 시작

        username_number = self.username_counters[museum]
        self.username_counters[museum] += 1  # 다음 유저를 위해 카운터 증가

        return f"익명{username_number}"

    async def connect(self, websocket: WebSocket, museum: str):
        origin = websocket.headers.get('origin')
        print(f"WebSocket origin: {origin}")  # Origin 값 로깅

        allowed_origins = ["http://43.201.93.53:8000"]  # 필요한 Origin만 추가

        # '*'이 포함되어 있으면 모든 Origin 허용
        if "*" not in allowed_origins and origin not in allowed_origins:
            await websocket.close(code=1008, reason="CORS policy violation")
            print("CORS policy violation: Connection closed")
            return

        await websocket.accept()

        if museum not in self.active_connections:
            self.active_connections[museum] = []

        self.active_connections[museum].append(websocket)
        username = self.generate_username(museum)  # 유저 이름을 자동으로 생성
        self.user_info[websocket] = (museum, username, None)  # `None`은 기본 artwork

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
        if websocket in self.user_info:
            museum, username, _ = self.user_info[websocket]
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

    async def broadcast(self, museum: str, message: dict):
        """특정 박물관 채팅방의 모든 사용자에게 메시지 전송"""
        if museum in self.active_connections:
            for connection in self.active_connections[museum]:
                await connection.send_json(message)

    def get_active_users(self, museum: str) -> List[str]:
        """특정 박물관 채팅방의 현재 접속자 목록"""
        if museum not in self.active_connections:
            return []
        return [self.user_info[ws][1] for ws in self.active_connections[museum]]

    def get_active_museums(self) -> List[str]:
        """현재 활성화된 박물관 채팅방 목록"""
        return list(self.active_connections.keys())

    async def update_artwork(self, websocket: WebSocket, new_artwork: str):
        """유저가 보는 작품을 변경하고, 해당 작품을 채팅방에 브로드캐스트"""
        if websocket in self.user_info:
            museum, username, _ = self.user_info[websocket]
            self.user_info[websocket] = (museum, username, new_artwork)  # Update artwork

            # 작품 변경 메시지 전송
            system_message = self.format_message(
                message_type="system",
                content=f"{username} is now viewing {new_artwork}",
                username="System",
                museum=museum,
                active_users=self.get_active_users(museum)
            )
            await self.broadcast(museum, system_message)

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

    async def add_message_to_history(self, museum: str, message: dict):
        """메시지를 저장소에 추가하고, 하루가 지난 메시지는 제거"""
        if museum not in self.message_history:
            self.message_history[museum] = []

        self.message_history[museum].append(message)

        # 오늘 날짜의 메시지만 유지
        today_str = date.today().isoformat()
        self.message_history[museum] = [
            msg for msg in self.message_history[museum]
            if msg["timestamp"].startswith(today_str)
        ]

    async def send_history(self, websocket: WebSocket, museum: str):
        """접속하는 유저에게 오늘의 메시지 히스토리 전송"""
        today_messages = [
            msg for msg in self.message_history.get(museum, [])
            if msg["timestamp"].startswith(date.today().isoformat())
        ]
        for message in today_messages:
            await websocket.send_json(message)

    async def cleanup_old_messages(self):
        """백그라운드 작업으로 오래된 메시지 정리"""
        while True:
            await asyncio.sleep(3600)  # 매시간 실행
            today_str = date.today().isoformat()
            for museum in self.message_history:
                self.message_history[museum] = [
                    msg for msg in self.message_history[museum]
                    if msg["timestamp"].startswith(today_str)
                ]

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
                username=manager.user_info[websocket][1],  # 유저 이름 가져오기
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

# 리다이렉트 경로 추가
@router.get("/chat/redirect/")
async def redirect_chat(request: Request):
    """
    /chat/redirect/ 경로로 들어오는 모든 요청을 /static/index.html로 리다이렉트합니다.
    쿼리 파라미터(Museum, artworkid)는 그대로 전달됩니다.
    """
    query = request.url.query
    redirect_url = f"/static/index.html?{query}" if query else "/static/index.html"
    return RedirectResponse(url=redirect_url)
