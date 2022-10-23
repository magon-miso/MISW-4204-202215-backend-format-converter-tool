import json
import time
import redis
import logging
from datetime import datetime
from notify import MailNotificator

colaredis = redis.Redis(host="redis-converter", port=6379, decode_responses=True, encoding="utf-8", )
consumer = colaredis.pubsub()
consumer.subscribe('sec')
mail_notificador = MailNotificator()

while True:
    message = consumer.get_message(ignore_subscribe_messages=True)
    time.sleep(3)
    logging.basicConfig(filename='converter.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.info('{} converter microservice running...'.format(datetime.now()))

    if message is None:
        continue

    print(str(datetime.now()) +"topic-sec: ", message)
    message_decoded = json.loads(message['data'])
    message_body = message_decoded['mensaje']
    receptores = message_decoded['receptores'].split(", ")

    for receptor in receptores:
        mail_notificador.send_mail(receptor, message_body)
