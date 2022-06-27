FROM python:3.7-slim

RUN mkdir /app

WORKDIR /app

COPY ./backend/requirements.txt ./
#COPY ./requirements.txt ./


RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./ ./

CMD ["gunicorn", "foodgram-project.wsgi:application", "--bind", "0:8000" ]
