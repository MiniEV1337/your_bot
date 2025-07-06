# bot/utils/html_utils.py

import re
from html import escape
from spellchecker import SpellChecker

# Инициализируем проверку орфографии
spell = SpellChecker(language='ru')

def correct_spelling(text: str) -> str:
    words = re.findall(r'\w+|\W+', text, re.UNICODE)
    corrected = []
    for word in words:
        if word.strip().isalpha() and word.lower() in spell.unknown([word]):
            corrected_word = spell.correction(word) or word
            corrected.append(corrected_word)
        else:
            corrected.append(word)
    return ''.join(corrected)

def clean_html(text: str) -> str:
    """
    Удаляет опасные HTML-теги и экранирует всё остальное.
    Поддерживаются только безопасные теги Telegram: <b>, <i>, <u>, <s>, <code>, <pre>, <blockquote>
    """
    allowed_tags = {"b", "strong", "i", "em", "u", "ins", "s", "strike", "del", "code", "pre", "blockquote"}

    def remove_tag(match):
        tag = match.group(1).lower()
        return match.group(0) if tag in allowed_tags else ''

    # Удаляем все теги, кроме разрешённых
    text = re.sub(r'</?([a-zA-Z0-9]+)(\s[^>]*)?>', remove_tag, text)

    # Экранируем одиночные < и > вне тегов
    return escape(text, quote=False)
