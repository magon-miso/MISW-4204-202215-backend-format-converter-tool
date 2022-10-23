# pull official base image
FROM python:3.7-alpine

# set work directory
WORKDIR /usr/src/app

RUN apk add ffmpeg

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
#COPY ./ /usr/src/app/
ADD ./ /usr/src/app/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
# RUN python converter/app.py
# CMD [ "python", "converter/app.py"]
# ENTRYPOINT ["python", "converter/app.py"]
