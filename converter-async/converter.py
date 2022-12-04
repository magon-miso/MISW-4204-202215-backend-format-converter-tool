import os
import json
import base64
from datetime import datetime
from pydub import AudioSegment
from correo import EmailSender
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from google.cloud import storage
#from google.cloud import pubsub_v1
#from concurrent.futures import TimeoutError

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

mail = EmailSender()
print('{} converter-async started'.format(datetime.now()))


@app.route("/", methods=["POST"])
def worker():
    envelope = request.get_json()
    if not envelope:
        msg = "no pub/sub message received"
        print(f"converter-async error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid pub/sub message format"
        print(f"converter-async error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]
    # print('{} converter-async audio-topic: {} '.format(datetime.now(), pubsub_message))
    data_task =  base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()
    # print('{} converter-async audio-topic: {} '.format(datetime.now(), json.loads(data_task)))

    message_decoded = json.loads(data_task) # message.data, message['data']
    task_id = message_decoded['id']
    filename = message_decoded['filename']
    newformat = message_decoded['newformat']
    uploadtime = message_decoded['upload_date']
    username = message_decoded['username']
    email = message_decoded['email']
    print('{} converter-async audio-topic: {} {} {} {} {}'.format(datetime.now(), task_id, uploadtime, filename, newformat, email))

    format = filename[len(filename)-3:]
    upload = datetime.strptime(uploadtime, '%Y-%m-%d %H:%M:%S')
    print('{} converter-async {} {}->{} init'.format(uploadtime, task_id, format, newformat))

    print('{} converter-async {} {}->{} bucket {}'.format(uploadtime, task_id, format, newformat, filename))
    storage_client = storage.Client()

    bucket = storage_client.bucket(app.config['BUCKET'])
    blob = bucket.blob(filename)
    print('{} converter-async {} {}->{} bucket {}'.format(uploadtime, task_id, format, newformat, filename))
    blob.download_to_filename(filename)
    print('{} converter-async {} {}->{} downloaded'.format(uploadtime, task_id, format, newformat))

    song = None
    if(format=="mp3"):
        song = AudioSegment.from_mp3(filename)
    elif(format=="wav"):
        song = AudioSegment.from_wav(filename)
    elif(format=="ogg"):
        song = AudioSegment.from_ogg(filename)

    filename2 = filename.replace("."+format, "."+newformat)
    print('{} converter-async {} {}->{} export init {}'.format(uploadtime, task_id, format, newformat, filename2))    
    song.export(filename2, format=newformat)
    diff_time = datetime.now() - upload
    print('{} converter-async {} {}->{} exported {}'.format(uploadtime, task_id, format, newformat, diff_time))

    blob_proc = bucket.blob(filename2)
    blob_proc.upload_from_filename(filename2)
    blob.make_public()
    print('{} converter-async {} {}->{} uploaded'.format(uploadtime, task_id, format, newformat))

    task = db.session.query(Task).filter(Task.id==task_id).first()
    task.status = "processed"
    task.processed_date = datetime.now()
    db.session.add(task)
    db.session.commit()
    print('{} converter-async {} {}->{} update {}'.format(uploadtime, task_id, format, newformat, diff_time))

    email_subject = filename +"  processed to "+ newformat
    email_message = username +", your audio file "+ filename +" has been processed to "+ newformat +" succesfully"

    if(app.config['EMAIL_ENABLED']=='true'):
        mail.send_mail(email, email_subject, email_message)
        print('converter-async {}->{} sent'.format(format, newformat))

    return ("", 204)
