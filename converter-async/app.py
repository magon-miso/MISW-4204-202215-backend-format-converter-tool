import json
import time
import redis
from datetime import datetime
from email import MailSender

colaredis = redis.Redis(host="localhost", port=6379, decode_responses=True, encoding="utf-8", )
consumer = colaredis.pubsub()
consumer.subscribe('audio')
mail = MailSender()

while True:
    message = consumer.get_message(ignore_subscribe_messages=True)
    time.sleep(1)
    if message is None:
        continue

    print(str(datetime.now()) +"topic-sec: ", message)
    message_decoded = json.loads(message['data'])
    message_body = message_decoded['mensaje']
    receptores = message_decoded['receptores'].split(", ")

    for receptor in receptores:
        mail.send_mail(receptor, message_body)
