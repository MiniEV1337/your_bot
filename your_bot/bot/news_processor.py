from ai_engine.summarizer import NewsSummarizer
from bot.html_formatter import render_news
import os

summarizer = NewsSummarizer(api_key=os.getenv("TOGETHER_API_KEY"))

def handle_news(news_text: str) -> str:
    try:
        summary = summarizer.summarize_news(news_text)
        return render_news("Срочная новость", summary)
    except Exception as e:
        print(f"[ERROR] Failed to summarize news: {e}")
        return "⚠️ Не удалось обработать новость."
