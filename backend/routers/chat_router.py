from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Dict
from datetime import datetime
from services.chat_services import format_message, validate_username, validate_museum_name

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_info: Dict[WebSocket, tuple] = {}  # (museum, username, artwork)

    async def connect(self, websocket: WebSocket, museum: str, username: str):
        if not validate_museum_name(museum):
            raise HTTPException(status_code=400, detail="Invalid museum name")
        if not validate_username(username):
            raise HTTPException(status_code=400, detail="Invalid username")
            
        # CORS check (if needed)
        origin = websocket.headers.get('origin')
        allowed_origins = ["http://43.201.93.53:8000", "http://localhost:8000", "*"]  # 원하는 CORS origin 설정

        if origin not in allowed_origins:
            raise HTTPException(status_code=403, detail="CORS policy violation")
        
        await websocket.accept()
        
        if museum not in self.active_connections:
            self.active_connections[museum] = []
        
        self.active_connections[museum].append(websocket)
        self.user_info[websocket] = (museum, username, None)  # `None` is the default for artwork
        
        # 입장 메시지 전송
        system_message = format_message(
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
            system_message = format_message(
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

manager = ConnectionManager()

@router.websocket("/ws/{museum}/{username}")
async def websocket_endpoint(
    websocket: WebSocket, 
    museum: str, 
    username: str
):
    await manager.connect(websocket, museum, username)
    try:
        while True:
            data = await websocket.receive_text()
            message = format_message(
                message_type="message",
                content=data,
                username=username,
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
    if not validate_museum_name(museum):
        raise HTTPException(status_code=400, detail="Invalid museum name")
        
    users = manager.get_active_users(museum)
    return {
        "museum": museum,
        "users": users,
        "total": len(users)
    }
