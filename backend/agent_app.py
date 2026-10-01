import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers import agent_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="Eyeson Agent Local Test")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/artChat_demo", StaticFiles(directory=os.path.join(STATIC_DIR, "artChat_demo")), name="artChat_demo")
app.mount("/artChat_css", StaticFiles(directory=os.path.join(STATIC_DIR, "artChat_css")), name="artChat_css")
app.mount("/artChat_js", StaticFiles(directory=os.path.join(STATIC_DIR, "artChat_js")), name="artChat_js")
app.include_router(agent_router.router, prefix="/agent", tags=["agent"])


@app.get("/", include_in_schema=False)
async def serve_root():
    return FileResponse(os.path.join(STATIC_DIR, "artChat_agent.html"))


@app.get("/artChatAgent", include_in_schema=False)
async def serve_art_chat_agent():
    return FileResponse(os.path.join(STATIC_DIR, "artChat_agent.html"))


@app.get("/artChat", include_in_schema=False)
async def serve_art_chat():
    return FileResponse(os.path.join(STATIC_DIR, "artChat.html"))
