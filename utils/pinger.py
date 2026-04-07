import aiohttp
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import RENDER_EXTERNAL_URL
import logging

logger = logging.getLogger(__name__)


async def ping_server():
    """Пингует сервер чтобы он не засыпал на Render"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RENDER_EXTERNAL_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    logger.info("✅ Server pinged successfully")
                else:
                    logger.warning(f"⚠️ Ping returned status {resp.status}")
    except Exception as e:
        logger.error(f"❌ Ping failed: {e}")


def start_pinger():
    """Запускает автопингер каждые 10 минут"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(ping_server, 'interval', minutes=10, id='server_pinger')
    scheduler.start()
    logger.info("🔄 Server pinger started (every 10 minutes)")
    return scheduler
