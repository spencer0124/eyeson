from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from routers import search_router, description_router, metadata_router, chat_router, manager

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
async def read_root():
    return RedirectResponse(url="/static/index.html")

@app.on_event("shutdown")
async def shutdown_event():
    await manager.shutdown()