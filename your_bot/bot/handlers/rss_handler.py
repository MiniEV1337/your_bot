# bot/handlers/rss_handler.py

from aiogram import Router, F
from aiogram.types import Message
from bot.data.rss_feeds import RSS_FEEDS
from bot.keyboards.topic_keyboard import keyboard_topics
from bot.utils.rss_parser import get_first_news
from bot.utils.together_api import translate_text, summarize_post
from bot.utils.html_utils import clean_html

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "Привет! 👋\nВыбери тему, чтобы получить свежую новость:",
        reply_markup=keyboard_topics
    )

@router.message(F.text.in_(RSS_FEEDS))
async def handle_topic(message: Message):
    topic = message.text
    feeds = RSS_FEEDS.get(topic)

    await message.answer(f"📡 Ищу новости по теме: <b>{topic}</b>...", parse_mode="HTML")

    news = get_first_news(feeds)
    if not news:
        return await message.answer("🙁 Пока нет свежих новостей по этой теме.")

    try:
        summary_ru = await translate_text(news["summary"])
        post = await summarize_post(news["title"], summary_ru)
        post_clean = clean_html(post)

        await message.answer(post_clean, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"⚠️ Ошибка генерации поста:\n<code>{e}</code>", parse_mode="HTML")
