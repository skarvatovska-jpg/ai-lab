"""
Головний файл для запуску Career-TwinNavigatorBot
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, check_config
from database import Database
from bot.handlers import router as main_router
from bot.twin_survey import router as twin_survey_router

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Головна функція запуску бота"""
    logger.info("Запуск Career-TwinNavigatorBot...")
    
    # Перевірка конфігурації
    try:
        check_config()
    except ValueError as e:
        logger.error(str(e))
        return
    
    # Ініціалізація бота та диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Підключення роутерів з обробниками
    dp.include_router(main_router)
    dp.include_router(twin_survey_router)
    
    # Ініціалізація бази даних
    db = Database()
    await db.init_db()
    logger.info("База даних ініціалізована")
    
    try:
        # Запуск бота
        logger.info("Бот готовий до роботи!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Помилка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено користувачем")

