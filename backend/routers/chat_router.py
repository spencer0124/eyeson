from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict
from datetime import datetime

router = APIRouter()

# ConnectionManager 클래스
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_info: Dict[WebSocket, tuple] = {}  # (museum, username, artwork)
        self.username_counters: Dict[str, int] = {}  # 박물관별 유저 이름 카운터

    def generate_username(self, museum: str) -> str:
        """박물관별로 유저 이름을 자동으로 생성 ('익명1', '익명2'...)"""
        if museum not in self.username_counters:
            self.username_counters[museum] = 1  # 최초 연결 시 카운터를 1로 시작
        
        username_number = self.username_counters[museum]
        self.username_counters[museum] += 1  # 다음 유저를 위해 카운터 증가
        
        return f"익명{username_number}"

    async def connect(self, websocket: WebSocket, museum: str):
        username = self.generate_username(museum)  # 유저 이름을 자동으로 생성
        
        # CORS check (if needed)
        origin = websocket.headers.get('origin')
        allowed_origins = ["http://43.201.93.53:8000", "http://0.0.0.0:8000", "*"]  # 원하는 CORS origin 설정

        if origin not in allowed_origins:
            raise HTTPException(status_code=403, detail="CORS policy violation")
        
        await websocket.accept()
        
        if museum not in self.active_connections:
            self.active_connections[museum] = []
        
        self.active_connections[museum].append(websocket)
        self.user_info[websocket] = (museum, username, None)  # `None` is the default for artwork
        
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

manager = ConnectionManager()

@router.websocket("ws/{museum}")
async def websocket_endpoint(websocket: WebSocket, museum: str):
    await manager.connect(websocket, museum)
    try:
        while True:
            data = await websocket.receive_text()
            message = manager.format_message(
                message_type="message",
                content=data,
                username=manager.user_info[websocket][1],  # 유저 이름 가져오기
                museum=museum,
                active_users=manager.get_active_users(museum)
            )
            await manager.broadcast(museum, message)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

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