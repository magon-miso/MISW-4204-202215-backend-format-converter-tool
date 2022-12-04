# pull official base image
FROM python:3.10-slim

# EXPOSE 8080

ENV APP_HOME /converter
WORKDIR $APP_HOME
COPY . ./

# RUN apk add ffmpeg
# RUN apk add build-base linux-headers
# RUN apk add libpq-dev

# RUN set -x  && add-apt-repository ppa:mc3man/trusty-media && apt-get update && apt-get dist-upgrade && apt-get install -y --no-install-recommends ffmpeg
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
CMD ["gunicorn", "--workers=2", "--threads=2", "--bind", "0.0.0.0:5000", "converter:app"]
