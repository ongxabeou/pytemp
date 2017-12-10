FROM python:3.5.3
LABEL maintainer="dm-ai-api"

COPY . /opt/dm.ai
WORKDIR /opt/dm.ai

RUN pip install -r requirements.txt

