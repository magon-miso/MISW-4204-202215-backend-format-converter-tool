# pull official base image
FROM python:3.7-alpine

# set work directory
WORKDIR /usr/src/app

RUN apk add ffmpeg

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/
# ADD ./ /usr/src/app/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# ENTRYPOINT [ "gunicorn", "--bind" , "0.0.0.0:5000", "manage:app"]
# CMD ["python", "converter/app.py"]
