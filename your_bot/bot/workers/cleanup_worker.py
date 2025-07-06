import asyncio
from datetime import datetime, timedelta
from bot.db.database import Session
from bot.models import News
from bot.config import logger

async def cleanup_old_news():
    session = Session()
    try:
        threshold = datetime.now() - timedelta(hours=48)
        deleted = session.query(News).filter(News.published < threshold).delete()
        session.commit()
        logger.info(f"🧹 Удалено {deleted} устаревших новостей")
    except Exception as e:
        logger.error(f"Ошибка автоудаления: {e}")
    finally:
        session.close()

async def cleanup_loop():
    while True:
        await cleanup_old_news()
        await asyncio.sleep(3600)  # раз в час

if __name__ == "__main__":
    asyncio.run(cleanup_loop())
