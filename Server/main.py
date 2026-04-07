import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from database.db import init_db
from handlers import start, auth, profile
from utils.pinger import start_pinger
from api.routes import setup_api_routes
from aiohttp import web

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрация обработчиков
dp.include_router(start.router)
dp.include_router(auth.router)
dp.include_router(profile.router)


async def set_commands():
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="help", description="Справка"),
    ]
    await bot.set_my_commands(commands)


async def health_check(request):
    """Endpoint для проверки здоровья сервера"""
    return web.Response(text="OK", status=200)


async def main():
    """Главная функция"""
    logger.info("🚀 Запуск Telegram бота...")
    
    # Инициализация БД
    init_db()
    logger.info("✅ База данных инициализирована")
    
    # Установка команд
    await set_commands()
    logger.info("✅ Команды установлены")
    
    # Запуск автопингера
    pinger = start_pinger()
    
    # Запуск веб-сервера для health check и API
    app = web.Application()
    app.router.add_get('/health', health_check)
    setup_api_routes(app)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    logger.info("🌐 Веб-сервер запущен на порту 8000")
    logger.info("📡 API доступен по адресу http://localhost:8000/api")
    
    # Запуск polling
    try:
        logger.info("📡 Бот начал слушать сообщения...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        pinger.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
