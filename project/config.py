"""
Конфігурація для Career-TwinNavigatorBot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# База даних
DATABASE_PATH = os.getenv("DATABASE_PATH", "career_twin.db")

# OpenAI модель
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Перевірка наявності обов'язкових ключів (тільки при запуску, не при імпорті)
def check_config():
    """Перевіряє наявність обов'язкових налаштувань"""
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        raise ValueError(
            "BOT_TOKEN не встановлено! Створіть .env файл з BOT_TOKEN=your_token\n"
            "Інструкції: дивіться README_IMPLEMENTATION.md або QUICKSTART.md"
        )
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        raise ValueError(
            "OPENAI_API_KEY не встановлено! Створіть .env файл з OPENAI_API_KEY=your_key\n"
            "Інструкції: дивіться README_IMPLEMENTATION.md або QUICKSTART.md"
        )

