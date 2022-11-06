FROM python:3.10.6-alpine
LABEL maintainer="sergryap@gmail.com"
RUN apk update && apk upgrade && apk add bash
WORKDIR /app
COPY . .
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN python3 -m venv venv
RUN source /venv/bin/activate
RUN pip3 install -r requirements.txt
CMD python3 /bot_tg.py | python3 /bot_vk.py