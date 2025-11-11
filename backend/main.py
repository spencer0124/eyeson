# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from routers import search_router, description_router, metadata_router, chat_router
# from routers.chat_router import manager

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     manager.start_scheduler()  # 스케줄러 명시적으로 시작
#     yield  # 애플리케이션이 실행되는 동안 여기서 멈춤
#     manager.scheduler.shutdown(wait=False)  # 스케줄러 종료

# app = FastAPI(lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 모든 도메인에서 요청 허용
#     allow_credentials=True,
#     allow_methods=["*"],  # 모든 HTTP 메서드 허용
#     allow_headers=["*"],  # 모든 헤더 허용
# )

# print("0709 testing")
# print("search router",search_router.router)

# # Include routers
# app.include_router(search_router.router, prefix="/search", tags=["search"])
# app.include_router(description_router.router, prefix="/description", tags=["description"])
# app.include_router(metadata_router.router, prefix="/metadata", tags=["metadata"])
# app.include_router(chat_router.router, prefix="/chat", tags=["chat"])

# @app.get("/")
# async def root():
#     return {"message": "FastAPI is running"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from routers import search_router, description_router, metadata_router, chat_router
from routers.chat_router import manager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print('base dir', BASE_DIR)
STATIC_DIR = os.path.join(BASE_DIR, "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    manager.start_scheduler()
    yield
    manager.scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# index.html 반환
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# /artChat 경로 추가
@app.get("/artChat", include_in_schema=False)
async def serve_art_chat():
    return FileResponse(os.path.join(STATIC_DIR, "artChat.html"))

app.mount("/modules", StaticFiles(directory="node_modules"), name="modules")

# 라우터 포함
app.include_router(search_router.router, prefix="/search", tags=["search"])
app.include_router(description_router.router, prefix="/description", tags=["description"])
app.include_router(metadata_router.router, prefix="/metadata", tags=["metadata"])
app.include_router(chat_router.router, prefix="/chat", tags=["chat"])