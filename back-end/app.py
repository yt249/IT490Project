import pika
import psycopg2
import os
import time
import logging
import json

# tag::process_request[]
def process_request(ch, method, properties, body):
    """
    Gets a request from the queue, acts on it, and returns a response to the
    reply-to queue
    """
    request = json.loads(body)
    if 'action' not in request:
        response = {
            'success': False,
            'message': "Request does not have action"
        }
    else:
        action = request['action']
        if action == 'GETHASH':
            data = request['data']
            email = data['email']
            logging.info(f"GETHASH request for {email} received")
            curr.execute('SELECT hash FROM users WHERE email=%s;', (email,))
            row =  curr.fetchone()
            if row == None:
                response = {'success': False}
            else:
                response = {'success': True, 'hash': row[0]}
        elif action == 'REGISTER':
            data = request['data']
            email = data['email']
            hashed = data['hash']
            logging.info(f"REGISTER request for {email} received")
            curr.execute('SELECT * FROM users WHERE email=%s;', (email,))
            if curr.fetchone() != None:
                response = {'success': False, 'message': 'User already exists'}
            else:
                curr.execute('INSERT INTO users VALUES (%s, %s);', (email, hashed))
                conn.commit()
                response = {'success': True}
        else:
            response = {'success': False, 'message': "Unknown action"}
    logging.info(response)
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(response)
    )
# end::process_request[]

logging.basicConfig(level=logging.INFO)

# repeatedly try to connect to db and messaging, waiting up to 60s, doubling
# backoff
wait_time = 1
while True:
    logging.info(f"Waiting {wait_time}s...")
    time.sleep(wait_time)
    if wait_time < 60:
        wait_time = wait_time * 2
    else:
        wait_time = 60
    try:
        logging.info("Connecting to the database...")
        postgres_password = os.environ['POSTGRES_PASSWORD']
        conn = psycopg2.connect(
            host='db',
            database='it490',
            user='postgres',
            password=postgres_password
        )

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

        break
    except psycopg2.OperationalError:
        print(f"Unable to connect to database.")
        continue
    except pika.exceptions.AMQPConnectionError:
        print("Unable to connect to messaging.")
        continue
curr = conn.cursor()
channel = connection.channel()

# create the request queue if it doesn't exist
channel.queue_declare(queue='request')

channel.basic_consume(queue='request', auto_ack=True,
                      on_message_callback=process_request)

# loops forever consuming from 'request' queue
logging.info("Starting consumption...")
channel.start_consuming()
