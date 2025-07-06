import asyncio
from aiogram import Bot
from database import Session, User
from bot.user_manager import get_favorites, is_night_enabled, get_subscription

# 🔧 Здесь должна быть твоя логика получения свежей новости
async def get_fresh_news_for(category: str) -> str:
    # Заглушка — вставь интеграцию с worker или TogetherAI
    return f"📣 Свежая новость по теме {category}!"

async def auto_news_sender(bot: Bot):
    while True:
        session = Session()
        users = session.query(User).filter(User.subscription_level > 0).all()

        for user in users:
            user_id = user.telegram_id
            level = user.subscription_level
            now_hour = int(asyncio.get_event_loop().time() // 3600 % 24)

            # Ночные ограничения
            if not is_night_enabled(user_id) and (now_hour < 7 or now_hour >= 22):
                continue

            favorites = get_favorites(user_id)
            limit = 3 if level == 1 else 6
            for category in favorites[:limit]:
                news = await get_fresh_news_for(category)
                try:
                    await bot.send_message(user_id, news)
                except Exception:
                    pass  # user blocked bot, etc.

        session.close()
        await asyncio.sleep(600)  # каждые 10 минут
