import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from handlers import register_handlers
from .auto_sender import auto_news_sender
from bot.news_processor import handle_news  # если нужен

# Загрузка env-файла
load_dotenv(dotenv_path=".env.docker")

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

register_handlers(dp)

async def main():
    logging.basicConfig(level=logging.INFO)

    # Запускаем фоновую авторассылку
    asyncio.create_task(auto_news_sender(bot))

    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
