import feedparser
import asyncio
import hashlib
from datetime import datetime
from database import Session, User, News  # модель News нужно добавить
from bot.user_manager import get_favorites, get_subscription, is_night_enabled
from bot.bot_instance import bot  # вынеси объект бота отдельно
from rss_feeds import RSS_FEEDS

async def parse_and_distribute():
    seen = set()

    session = Session()

    for category, urls in RSS_FEEDS.items():
        for url in urls:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                uid = hashlib.md5((entry.link).encode()).hexdigest()
                if session.query(News).filter_by(uid=uid).first():
                    continue

                title = entry.title
                link = entry.link
                published = entry.get("published", str(datetime.now()))
                summary = entry.get("summary", "")

                # 💾 Сохраняем новость
                news = News(
                    uid=uid,
                    title=title,
                    link=link,
                    category=category,
                    summary=summary,
                    published=published
                )
                session.add(news)
                session.commit()

                # 📣 Рассылаем премиумам
                users = session.query(User).filter(User.subscription_level == 2).all()
                for user in users:
                    if not is_night_enabled(user.telegram_id):
                        now = datetime.now().hour
                        if now < 7 or now > 22:
                            continue
                    favorites = get_favorites(user.telegram_id)
                    if category_code(category) in favorites:
                        try:
                            msg = f"<b>{title}</b>\n{link}"
                            await bot.send_message(user.telegram_id, msg, parse_mode="HTML")
                        except Exception:
                            continue

    session.close()

def category_code(label):
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
    return mapping.get(label, "other")

async def main():
    while True:
        try:
            await parse_and_distribute()
        except Exception as e:
            print(f"[!] Ошибка: {e}")
        await asyncio.sleep(600)  # каждые 10 минут

if __name__ == "__main__":
    asyncio.run(main())
