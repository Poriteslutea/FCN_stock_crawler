import time
import pika
from config import MQ_PASSWORD, MQ_USER
from stock_crawler.data_factory import generate_sample_data, generate_next_random
credentials = pika.PlainCredentials(MQ_USER, MQ_PASSWORD)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='streaming')

def gen_data_task():
    # Read the last result from queue
    method_frame, header_frame, body = channel.basic_get(queue='streaming')
    print(method_frame, header_frame, body)
    
    if method_frame:
        last_result = str(body.decode())
        print("Last result:", last_result)
    else:
        last_result = '100.0 100.0 100.0'
        print("First run")
    
    # Simulate some task and generate a new result
    arr = [float(i) for i in last_result.split()]
    print(arr)
    new_vals = generate_next_random(arr, 'D')
    new_vals_str_arr = [str(round(v, 2)) for v in new_vals]
    new_result = ' '.join(new_vals_str_arr)
    print("New result:", new_result)

    
    # Publish the new result to the queue
    channel.basic_publish(exchange='',
                          routing_key='streaming',
                          body=str(new_result))
    

while True:
    gen_data_task()
    time.sleep(15)
