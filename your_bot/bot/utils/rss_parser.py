# bot/utils/rss_parser.py

import feedparser
import re
from rapidfuzz import fuzz

def get_first_news(feeds: list[str]) -> dict | None:
    seen_titles = []
    for url in feeds:
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            title = entry.get("title", "").strip()
            if any(fuzz.ratio(title, t) > 85 for t in seen_titles):
                continue
            seen_titles.append(title)

            summary = entry.get("summary", "") or entry.get("description", "")
            image_url = None

            # Ищем изображение
            if entry.get("media_content"):
                image_url = entry.media_content[0].get("url")
            elif entry.get("media_thumbnail"):
                image_url = entry.media_thumbnail[0].get("url")
            elif entry.get("enclosures"):
                for e in entry.enclosures:
                    if e.get("type", "").startswith("image"):
                        image_url = e.get("href")
                        break
            elif "img" in summary:
                match = re.search(r'<img[^>]+src="([^"]+)"', summary)
                if match:
                    image_url = match.group(1)

            return {
                "title": title,
                "summary": summary,
                "link": entry.get("link"),
                "image_url": image_url
            }
    return None
