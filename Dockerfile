FROM python:3.8

COPY . /app

WORKDIR /app

ENV RABBITHOST localhost
ENV RABBITPORT 5672
ENV YOUR_API_KEY 

RUN pip install -r requirements.txt

COPY . /app

CMD python location.py