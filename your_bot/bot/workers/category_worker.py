import asyncio
import argparse
import feedparser
import hashlib
from datetime import datetime

from bot.bot_instance import bot
from bot.config import logger
from bot.user_manager import get_favorites
from bot.db.database import Session
from bot.models import News, User
from data.rss_feeds import RSS_FEEDS


def label_to_code(label: str) -> str:
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
    reverse = {v: k for k, v in mapping.items()}
    return reverse.get(label, None), label


async def process_category(code: str):
    session = Session()
    label = None

    # Найдём соответствующий emoji-label для категории
    for lbl, urls in RSS_FEEDS.items():
        if label_to_code(lbl) == code:
            label = lbl
            break

    if not label or label not in RSS_FEEDS:
        logger.error(f"⚠️ Категория {code} не найдена в RSS_FEEDS")
        return

    for url in RSS_FEEDS[label]:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                uid = hashlib.md5(entry.link.encode()).hexdigest()

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

                for user in session.query(User).filter(User.subscription_level == 2).all():
                    if code in get_favorites(user.telegram_id):
                        try:
                            await bot.send_message(user.telegram_id, f"<b>{entry.title}</b>\n{entry.link}", parse_mode="HTML")
                        except Exception as e:
                            logger.warning(f"Не отправлено {user.telegram_id}: {e}")
        except Exception as e:
            logger.error(f"Парсинг {url} не удался: {e}")

    session.close()


async def category_loop(code: str):
    while True:
        await process_category(code)
        await asyncio.sleep(600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RSS воркер по категории")
    parser.add_argument("--category", required=True, help="Код категории (ai, crypto, etc.)")
    args = parser.parse_args()

    asyncio.run(category_loop(args.category))
