FROM python:3.7-slim-stretch
RUN mkdir -p /code
COPY . /code
WORKDIR /code
ENV TEAM_NAME "CC_0118_0770"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN pip install -r requirements.txt
