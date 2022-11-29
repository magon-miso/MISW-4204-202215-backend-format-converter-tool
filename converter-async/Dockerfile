# pull official base image
# FROM python:3.7-alpine
FROM python:3.10-slim

# set work directory
# WORKDIR /usr/src/app

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apk add ffmpeg
RUN apk add build-base linux-headers
RUN apk add libpq-dev

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

# two entrypoints: converter async + monitor 
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
CMD ["python", "app.py"]
