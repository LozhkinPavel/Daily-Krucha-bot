FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3.11 python3.11-distutils
RUN apt-get install -y python3-pip
RUN pip install redis
RUN pip install pyTelegramBotAPI
RUN pip install schedule
CMD ["python3", "data/main.py"]