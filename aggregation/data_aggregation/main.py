# Aggregation of the processed-data from kafka

import logging
import json
import faust
from prometheus_client import Counter, start_http_server

SERVICE_NAME = "data_aggregation"

# Event counter for monitoring with prometheus
# The received sensor values
SENSOR_VALUES_COUNT = Counter("sensor_values_received", "The number of sensor-data values received from processed-data topic")
# The aggregated sensor values
AGGREGATED_VALUES_COUNT = Counter("sensor_values_aggregated", "The number of sensor-data values aggregated")
# The sent sensor values
SENT_VALUES_COUNT = Counter("sensor_values_sent", "The number of sensor-data values sent to aggregated-data (changelog) topic")

# Configure the logging mechanism
logging.basicConfig(
    # Default Level
    level = logging.INFO,
    # Formatting the logs
    format="%(asctime)s,%(msecs)d%(levelname)-8s[%(name)s:%(filename)s(%(lineno)d)]%(message)s")

# Get the logger
logger = logging.getLogger(__name__)

app = faust.App(SERVICE_NAME, broker="broker:29092", value_serializer='raw')
processed_data_topic = app.topic("processed-data", partitions=8)
aggregated_data_topic = app.topic("data_aggregation-average-changelog", partitions=8)

# Table for data aggregation (average temp)
average_table = app.Table('average', default=dict)

@app.agent(processed_data_topic)
async def on_event(stream) -> None:
    # Create additional topics
    await aggregated_data_topic.declare()
    async for msg_key, msg_value in stream.items():
        # At first imcrement the event counter for prometheus monitoring of the received sensor values
        SENSOR_VALUES_COUNT.inc()
        logger.info(f'Key: {msg_key} - Received new sensor value {msg_value}')
        serialized_message = json.loads(msg_value)
        # Aggregate the data of the specific sensor number: Average over the last 10 values (TODO: Over time better?)
        sensor_num = serialized_message['sensor_num']
        sensor_val = serialized_message['value']
        average_value = average_table.get(sensor_num, {})
        if average_value:
            average_value['history'].append(sensor_val)
            average_value['history'] = average_value['history'][-10:]
            average_value['average'] = round(sum(average_value['history']) / len(average_value['history']), 2)
        else:
            average_value['history'] = [sensor_val]
            average_value['average'] = sensor_val
        # Increment the prometheus counter for aggregated values
        AGGREGATED_VALUES_COUNT.inc()
        logger.info(f"Aggregated value: {average_value}")
        # write it back to the table (also updating changelog):
        average_table[sensor_num] = average_value
        # Increment the prometheus counter for sent values (via changelog topic of the app table)
        SENT_VALUES_COUNT.inc() 
        

@app.task
async def on_started() -> None:
    logger.info('Starting prometheus server to expose the metrics on port=7004')
    start_http_server(port=7004)
