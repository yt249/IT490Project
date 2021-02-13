import pika
import psycopg2
import os
import time
import logging
import json

def process_request(ch, method, properties, body):
    print(body)
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body='HELLO'
    )

logging.basicConfig(level=logging.INFO)

logging.info(f"Waiting 30s...")
time.sleep(30)

logging.info("Connecting to messaging service...")
credentials = pika.PlainCredentials(
    os.environ['RABBITMQ_DEFAULT_USER'],
    os.environ['RABBITMQ_DEFAULT_PASS']
)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
	host='messaging',
	credentials=credentials
    )
)

channel = connection.channel()
channel.queue_declare(queue='request')

channel.basic_consume(queue='request', auto_ack=True,
                      on_message_callback=process_request)

logging.info("Starting consumption...")
channel.start_consuming()
