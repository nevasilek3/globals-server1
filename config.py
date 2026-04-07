import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "8784838245:AAGEPzmdV0YsampdTKvUvwJgSXtCfzoW-cg")

# Database - SQLite для Render (бесплатный уровень)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bot_data.db")

# Render
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "https://globals-server1.onrender.com")

# Server
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

# Subscription plans (в днях)
SUBSCRIPTION_PLANS = {
    "7_days": {"days": 7, "price": 100},
    "30_days": {"days": 30, "price": 350},
    "90_days": {"days": 90, "price": 900},
}
