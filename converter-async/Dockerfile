# pull official base image
FROM python:3.7-alpine

# set work directory
WORKDIR /usr/src/app

RUN apk add ffmpeg
RUN apk add build-base linux-headers

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

# two entrypoints: converter async + monitor 
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

CMD ["python", "app.py"]
