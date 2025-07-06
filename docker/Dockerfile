FROM python:3.11
WORKDIR /app

COPY ./bot /app
COPY ./requirements.txt /app
COPY ../supervisord.conf /app


RUN pip install -r requirements.txt
RUN pip install supervisor

CMD ["python", "start_supervisor.py"]

