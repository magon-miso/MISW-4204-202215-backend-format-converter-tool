# pull official base image
FROM python:3.10-slim

ENV APP_HOME /converter
WORKDIR $APP_HOME
COPY . ./

RUN apk add ffmpeg
RUN apk add build-base linux-headers
RUN apk add libpq-dev

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
