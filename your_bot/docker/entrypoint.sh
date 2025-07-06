#!/bin/bash

echo "⏳ Ожидаем подключение к PostgreSQL..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  sleep 1
done

echo "✅ PostgreSQL доступен"
echo "🚀 Применяем Alembic миграции..."
alembic -c /app/alembic.ini upgrade head

echo "📦 Запускаем Telegram-бота"

# Устанавливаем PYTHONPATH, чтобы импорты типа `from bot...` сработали
export PYTHONPATH=/app

# Ищем main.py и запускаем его
if [ -f /app/bot/main.py ]; then
    exec python /app/bot/main.py
elif [ -f /app/main.py ]; then
    exec python /app/main.py
else
    echo "❌ main.py не найден ни в /app/bot/, ни в /app/"
    ls -la /app
    ls -la /app/bot || echo "⛔ Папки /app/bot нет"
    exit 1
fi
