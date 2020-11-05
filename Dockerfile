FROM python:3.8

COPY . /app

WORKDIR /app

ENV RABBITHOST 172.17.0.2
ENV RABBITPORT 5672
ENV YOUR_API_KEY AIzaSyC8zHDqr2XwpSKSiJgkRcnUI7I0c018k80

RUN pip install -r requirements.txt

COPY . /app

CMD ["python","-u","location.py"]
