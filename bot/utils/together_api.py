# bot/utils/together_api.py

import os
import aiohttp
import logging

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "meta-llama/Llama-3-8b-chat-hf",
    "openchat/openchat-3.5-1210"
]

async def together_call(prompt: str, model_override: str = None) -> str:
    models = MODELS.copy()

    if model_override and model_override in models:
        models.remove(model_override)
        models.insert(0, model_override)

    try:
        with open("last_model.txt", "r", encoding="utf-8") as f:
            last = f.read().strip()
            if last in models:
                models.remove(last)
                models.insert(0, last)
    except FileNotFoundError:
        pass

    for model in models:
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 500
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload) as resp:
                    response = await resp.json()
                    if "choices" in response:
                        with open("last_model.txt", "w", encoding="utf-8") as f:
                            f.write(model)
                        return response["choices"][0]["message"]["content"]
        except Exception as e:
            logging.warning(f"[Together] ❌ Ошибка {model}: {e}")
            continue

    raise Exception("🚫 Все модели Together недоступны")

async def translate_text(text: str) -> str:
    prompt = f"Переведи на русский:\n\n{text}"
    return await together_call(prompt)

async def summarize_post(title: str, summary_ru: str) -> str:
    prompt = f"""
Ты — Telegram-блогер. Сформулируй пост на русском языке в формате HTML. Структура:
<b>Заголовок</b> — короткий, без слов "Заголовок"
<i>Цитата</i> — одно предложение, передающее суть
Эмодзи по смыслу
1–3 хэштега через пробел (в конце)

Только теги: <b>, <i>, <u>, <s>, <code>, <pre>, <blockquote>. Без ссылок. Без "цитат" и меток.

Заголовок: {title}
Содержание: {summary_ru}
"""
    return await together_call(prompt)
