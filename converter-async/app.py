import os
import json
import time
#import redis
import logging
from enum import Enum
from datetime import datetime
from pydub import AudioSegment
from correo import EmailSender
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from google.cloud import storage
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
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
    processed_date = db.Column(db.DateTime)


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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL_ASYNC")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EMAIL_ENABLED'] = os.getenv("EMAIL_ENABLED")
app.config['EMAIL_FROM'] = os.getenv("EMAIL_FROM")
app.config['EMAIL_PWD'] = os.getenv("EMAIL_PWD")
app.config['BUCKET'] = os.getenv("AUDIO_BUCKET")
app.config['PROJECT'] = os.getenv("PROJECT_ID")
app.config['TOPIC'] = os.getenv("TOPIC_ID")
app.config['SUBSCRIPTION'] = os.getenv("TOPIC_SUBSCRIPTION")

app_context = app.app_context()
app_context.push()
db.init_app(app)

# colaredis = redis.Redis(host="10.182.0.3", port=6379, decode_responses=True, encoding="utf-8", )
# consumer = colaredis.pubsub()
# consumer.subscribe('audio')
mail = EmailSender()

logging.basicConfig(filename='converter.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
print('{} converter-async started'.format(datetime.now()))
logging.info('converter-async started ...')

#def process_payload(message):
def process_payload(message: pubsub_v1.subscriber.message.Message) -> None:
    # print(f"Received {message.data}.")
    # print('{} converter-async audio-topic: {}'.format(datetime.now(), message.data))
    # logging.info('converter-async audio-topic: {}'.format(message.data))

    message_decoded = json.loads(message.data) # message['data']
    task_id = message_decoded['id']
    # filepath = message_decoded['filepath']
    filename = message_decoded['filename']
    newformat = message_decoded['newformat']
    uploadtime = message_decoded['upload_date']
    username = message_decoded['username']
    email = message_decoded['email']
    print('{} converter-async audio-topic: {} {} {} {} {}'.format(datetime.now(), task_id, uploadtime, filename, newformat, email))

    message.ack()
    print('{} converter-async {} {}->{} message ack sent'.format(datetime.now(), task_id, filename, newformat))
    logging.info('{} converter-async {} {}->{} message ack sent'.format(uploadtime, task_id, filename, newformat))

    song = None
    format = filename[len(filename)-3:]
    upload = datetime.strptime(uploadtime, '%Y-%m-%d %H:%M:%S')
    logging.info('{} converter-async {} {}->{} init'.format(uploadtime, task_id, format, newformat))

    logging.info('{} converter-async {} {}->{} bucket {}'.format(uploadtime, task_id, format, newformat, filename))
    storage_client = storage.Client()
    #storage_client = storage.Client(app.config['PROJECT_ID'])

    bucket = storage_client.bucket(app.config['BUCKET'])
    blob = bucket.blob(filename)
    logging.info('{} converter-async {} {}->{} bucket {}'.format(uploadtime, task_id, format, newformat, filename))
    blob.download_to_filename(filename)
    # print('{} converter-async {} {}->{} downloaded'.format(datetime.now(), task_id, format, newformat))
    logging.info('{} converter-async {} {}->{} downloaded'.format(uploadtime, task_id, format, newformat))

    if(format=="mp3"):
        song = AudioSegment.from_mp3(filename)
    elif(format=="wav"):
        song = AudioSegment.from_wav(filename)
    elif(format=="ogg"):
        song = AudioSegment.from_ogg(filename)

    filename2 = filename.replace("."+format, "."+newformat)
    logging.info('{} converter-async {} {}->{} export init {}'.format(uploadtime, task_id, format, newformat, filename2))    
    song.export(filename2, format=newformat)
    diff_time = datetime.now() - upload
    logging.info('{} converter-async {} {}->{} exported {}'.format(uploadtime, task_id, format, newformat, diff_time))

    blob_proc = bucket.blob(filename2)
    blob_proc.upload_from_filename(filename2)

    # print('{} converter-async {} {}->{} uploaded'.format(datetime.now(), task_id, format, newformat))
    logging.info('{} converter-async {} {}->{} uploaded'.format(uploadtime, task_id, format, newformat))

    with app_context:
        # processed task in postgress
        task = db.session.query(Task).filter(Task.id==task_id).first()
        task.status = "processed"
        task.processed_date = datetime.now()
        db.session.add(task)
        db.session.commit()
        print('{} converter-async {} {}->{} update {}'.format(datetime.now(), task_id, format, newformat, diff_time))
        logging.info('{} converter-async {} {}->{} update {}'.format(uploadtime, task_id, format, newformat, diff_time))

    email_subject = filename +"  processed to "+ newformat
    email_message = username +", your audio file "+ filename +" has been processed to "+ newformat +" succesfully"

    if(app.config['EMAIL_ENABLED']=='true'):
        mail.send_mail(email, email_subject, email_message)
        logging.info('converter-async {}->{} sent'.format(format, newformat))


timeout = 2
counter = 0
while True:
    counter+=1
    time.sleep(1)
    # message = consumer.get_message(ignore_subscribe_messages=True)

    # if (counter%15==0):
    #     logging.info('converter-async running ...')
    # if message is None:
    #     continue

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(app.config['PROJECT'], app.config['SUBSCRIPTION'])
    print('{} converter-async {} ...'.format(datetime.now(), subscription_path))
    logging.info('converter-async {} ...'.format(subscription_path))

    # flow_control = pubsub_v1.types.FlowControl(max_messages=2)
    # streaming_pull_future = subscriber.subscribe(subscription_path, callback=process_payload, flow_control=flow_control)
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=process_payload)

    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            # print('{} converter-async streaming_pull_future.result'.format(datetime.now()))
            streaming_pull_future.result(timeout=timeout)
            # streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel() # Trigger the shutdown.
            streaming_pull_future.result() # block until shutdown is complete
