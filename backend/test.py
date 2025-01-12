from routers.chat_router import manager
import asyncio

async def test_archive():
    await manager.archive_and_clear_old_messages()

asyncio.run(test_archive())