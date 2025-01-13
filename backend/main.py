from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from routers import search_router, description_router, metadata_router, chat_router
from routers.chat_router import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: initializing resources...")
    manager.start_scheduler()  # 스케줄러 명시적으로 시작

    yield  # 애플리케이션이 실행되는 동안 여기서 멈춤
    
    # 애플리케이션 종료 시 실행
    print("Application shutdown: cleaning up resources...")
    manager.scheduler.shutdown(wait=False)  # 스케줄러 종료

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# Mount static files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Include routers
app.include_router(search_router.router, prefix="/search", tags=["search"])
app.include_router(description_router.router, prefix="/description", tags=["description"])
app.include_router(metadata_router.router, prefix="/metadata", tags=["metadata"])
app.include_router(chat_router.router, prefix="/chat", tags=["chat"])

@app.get("/")
async def read_root(request: Request):
    query = request.url.query  # 쿼리 파라미터 가져오기
    # redirect_url = f"/static/index.html?{query}" if query else "/static/index.html"
    redirect_url = f"/static/temp.html"
    return RedirectResponse(url=redirect_url)