import os
import json
import time
import redis
import logging
from enum import Enum
from datetime import datetime
from pydub import AudioSegment
from correo import EmailSender
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

db = SQLAlchemy()

class Task(db.Model):
    #__tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128))
    newformat = db.Column(db.String(5))
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    #status = db.Column(Enum("uploaded", "processed", name='statusEnum'))
    status = db.Column(db.String(25))
    upload_date = db.Column(db.DateTime)

class User(db.Model):
    #__tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(250))
    #role = db.Column(Enum("ADMIN", "USER", name='RoleUser'))
    role = db.Column(db.String(25))
    tasks = db.relationship('Task', cascade='all, delete, delete-orphan')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL_ASYNC", "sqlite:///converter.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app_context = app.app_context()
app_context.push()
db.init_app(app)

colaredis = redis.Redis(host="10.182.0.3", port=6379, decode_responses=True, encoding="utf-8", )
#colaredis = redis.Redis(host="redis-converter", port=6379, decode_responses=True, encoding="utf-8", )
consumer = colaredis.pubsub()
consumer.subscribe('audio')
mail = EmailSender()

counter = 0
while True:
    counter+=1
    message = consumer.get_message(ignore_subscribe_messages=True)
    time.sleep(1)
    logging.basicConfig(filename='converter.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
    if (counter%10==0):
        logging.info('converter-async running ...')

    if message is None:
        continue

    logging.info('converter-async audio-topic: {}'.format(message))
    message_decoded = json.loads(message['data'])

    task_id = message_decoded['id']
    filepath = message_decoded['filepath']
    filename = message_decoded['filename']
    newformat = message_decoded['newformat']
    uploadtime = message_decoded['upload_date']
    username = message_decoded['username']
    email = message_decoded['email']

    song = None
    format = filename[len(filename)-3:]
    upload = datetime.strptime(uploadtime, '%Y-%m-%d %H:%M:%S')
    logging.info('{} converter-async {} {}->{} init'.format(uploadtime, task_id, format, newformat))

    if(format=="mp3"):
        song = AudioSegment.from_mp3(filepath)
    elif(format=="wav"):
        song = AudioSegment.from_wav(filepath)
    elif(format=="ogg"):
        song = AudioSegment.from_ogg(filepath)

    song.export(filepath.replace("."+format, "."+newformat), format=newformat)
    diff_time = datetime.now() - upload
    logging.info('{} converter-async {} {}->{} done {}'.format(uploadtime, task_id, format, newformat, diff_time))

    # processed task in postgress
    task = db.session.query(Task).filter(Task.id==task_id).first()
    task.status = "processed"
    db.session.add(task)
    db.session.commit()
    logging.info('{} converter-async {} {}->{} update {}'.format(uploadtime, task_id, format, newformat, diff_time))

    subject = filename +"  processed to "+ newformat
    message = username +", your audio file "+ filename +" has been processed to "+ newformat +" succesfully"
    # mail.send_mail(email, subject, message)
    # logging.info('{} converter-async {}->{} sent'.format(uploadtime, format, newformat))
