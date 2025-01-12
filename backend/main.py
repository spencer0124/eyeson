from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from routers import search_router, description_router, metadata_router, chat_router
from routers.chat_router import manager

app = FastAPI()

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
    redirect_url = f"/static/index.html?{query}" if query else "/static/index.html"
    return RedirectResponse(url=redirect_url)

@app.on_event("shutdown")
async def shutdown_event():
    print("서버가 종료됩니다.")
    manager.scheduler.shutdown(wait=False)  # 스케줄러 종료