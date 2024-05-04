from datetime import datetime
import plotly.graph_objects as go 
from IPython.display import display
import time
import pika
import pandas as pd
from datetime import datetime
from config import MQ_PASSWORD, MQ_USER


fig = go.FigureWidget()
fig.add_scatter(name='NO1', mode='lines+markers')
fig.add_scatter(name='NO2', mode='lines+markers')
fig.add_scatter(name='NO3', mode='lines+markers')

df = pd.DataFrame()

credentials = pika.PlainCredentials(MQ_USER, MQ_PASSWORD)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# Declare a queue
queue_name = 'streaming'
channel.queue_declare(queue=queue_name)  # Make sure the queue is durable

# Define a callback function to process incoming messages
def callback(ch, method, properties, body):
    global df
    data = body.decode()
    arr = {f'NO{i+1}': float(v) for i, v in enumerate(data.split())}
    t = datetime.now()
    new_df = pd.DataFrame(arr, index=[t])
    df = pd.concat([df, new_df], axis=0)

    
    with fig.batch_update():
        fig.data[0].x = df.index
        fig.data[1].x = df.index
        fig.data[2].x = df.index
        fig.data[0].y = df['NO1']
        fig.data[1].y = df['NO2']
        fig.data[2].y = df['NO3']
    print(df)
    fig.write_html('plot.html')



    ch.basic_ack(delivery_tag=method.delivery_tag)



# Start consuming messages from the queue
channel.basic_qos(prefetch_count=1)  # Only fetch one message at a time
channel.basic_consume(queue=queue_name, on_message_callback=callback)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()