FROM python:3.12

MAINTAINER "Karamolegkos Panagiotis"

WORKDIR /app

COPY . .

RUN apt update -y
RUN apt upgrade -y

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "server.py"]