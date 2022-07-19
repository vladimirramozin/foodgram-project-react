FROM python:3.7-slim

RUN mkdir /app

WORKDIR /app

COPY ./requirements.txt ./

#COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./ ./

#COPY ./backend ./

EXPOSE 8000

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
