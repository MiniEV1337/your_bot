import asyncio
import feedparser
import hashlib
from datetime import datetime
from bot.user_manager import get_subscription, get_favorites
from bot.config import logger
from bot.bot_instance import bot  # объект Bot должен быть импортирован отсюда
from data.rss_feeds import RSS_FEEDS
from data.database import Session
from data.models.news import News
from data.models.user import User


def category_code(label: str) -> str:
    mapping = {
        "🧠 Искусственный интеллект": "ai",
        "💻 Технологии": "technology",
        "🎮 Игры": "gaming",
        "📈 Крипта": "crypto",
        "🔬 Наука": "science",
        "📰 Политика": "politics",
        "📉 Экономика": "economy",
        "🎨 Культура": "culture",
        "🌍 Мир": "world",
        "🎬 Кино": "cinema",
        "🩺 Медицина": "medicine"
    }
    return mapping.get(label, "unknown")


async def parse_and_distribute():
    session = Session()
    for label, urls in RSS_FEEDS.items():
        code = category_code(label)
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    uid = hashlib.md5(entry.link.encode()).hexdigest()

                    # пропускаем если уже есть
                    if session.query(News).filter_by(uid=uid).first():
                        continue

                    news = News(
                        uid=uid,
                        title=entry.title,
                        link=entry.link,
                        category=code,
                        summary=entry.get("summary", "")[:1000],
                        published=datetime.now()
                    )
                    session.add(news)
                    session.commit()

                    # отсылаем премиумам
                    premium_users = session.query(User).filter(User.subscription_level == 2).all()
                    for user in premium_users:
                        favorites = get_favorites(user.telegram_id)
                        if code in favorites:
                            try:
                                text = f"<b>{entry.title}</b>\n{entry.link}"
                                await bot.send_message(user.telegram_id, text, parse_mode="HTML")
                            except Exception as e:
                                logger.warning(f"Не удалось отправить {user.telegram_id}: {e}")
            except Exception as e:
                logger.error(f"Ошибка парсинга {url}: {e}")
    session.close()


async def worker_loop():
    while True:
        await parse_and_distribute()
        await asyncio.sleep(600)  # каждые 10 минут


if __name__ == "__main__":
    asyncio.run(worker_loop())
