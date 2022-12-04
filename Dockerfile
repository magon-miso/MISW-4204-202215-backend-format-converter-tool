# pull official base image
# FROM python:3.7-alpine
FROM python:3.10-slim
# FROM python:3.11-slim-bullseye

# set work directory
# WORKDIR /usr/src/app

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# RUN apk add build-base linux-headers
# RUN apk add libpq-dev
# RUN apk add ffmpeg

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# ENV PYTHONUNBUFFERED True

# install dependencies
# COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy project
# COPY . /usr/src/app/

# two entrypoints: guicorn + monitor
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
CMD ["gunicorn", "--workers=5", "--threads=2", "--bind", "0.0.0.0:5000", "manage:app"]
