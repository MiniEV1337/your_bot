FROM python:3.11
WORKDIR /app

# Копируем код проекта
COPY ./bot /app/bot
COPY ./migrations /app/migrations
COPY ./requirements.txt /app
COPY ./alembic.ini /app/alembic.ini
COPY ./docker/supervisord.conf /app/supervisord.conf
COPY ./docker/entrypoint.sh /entrypoint.sh

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y postgresql-client
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install supervisor
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
