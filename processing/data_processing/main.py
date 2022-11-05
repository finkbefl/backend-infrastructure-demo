# Processing the src-data from kafka

import logging
import json
import faust
from prometheus_client import Counter, start_http_server

SERVICE_NAME = "data_processing"

# Event counter for monitoring with prometheus
# The received sensor values
SENSOR_VALUES_COUNT = Counter("sensor_values_received", "The number of sensor-data values received trom src_data topic")
# The processed sensor values
PROCESSED_VALUES_COUNT = Counter("sensor_values_processed", "The number of sensor-data values processed")
# The sent sensor values
SENT_VALUES_COUNT = Counter("sensor_values_sent", "The number of sensor-data values sent to processed-data topic")

# Configure the logging mechanism
logging.basicConfig(
    # Default Level
    level = logging.INFO,
    # Formatting the logs
    format="%(asctime)s,%(msecs)d%(levelname)-8s[%(name)s:%(filename)s(%(lineno)d)]%(message)s")

# Get the logger
logger = logging.getLogger(__name__)

app = faust.App(SERVICE_NAME, broker="broker:29092", value_serializer='raw')
src_data_topic = app.topic("src-data", partitions=8)
processed_data_topic = app.topic("processed-data", partitions=8)

def process_data_value(sensor_value):
    # TODO: Check for missing values, outliers, exceptions,...
    # TODO: Define a maximum number of values per a specific time? e.g. max. 1 Value per second, others will be rejected?
    # All sensor values are processed as integer, but maybe we will receive float numbers
    if is_float(sensor_value):
        logger.info(f'Sensor value of type float received, convert to int')
        return int(float(sensor_value))
    else:
        logger.info(f'Sensor value of type int received, no conversion')
        return int(sensor_value)

def is_float(value):
  try:
    float(value)
    return True
  except:
    return False

@app.agent(src_data_topic)
async def on_event(stream) -> None:
    # Create additional topics
    await processed_data_topic.declare()
    async for msg_key, msg_value in stream.items():
        # At first imcrement the event counter for prometheus monitoring of the received sensor values
        SENSOR_VALUES_COUNT.inc()
        logger.info(f'Key: {msg_key} - Received new sensor value {msg_value}')
        serialized_message = json.loads(msg_value)
        # Process the data (cast float sensor values to int)
        serialized_message['value'] = process_data_value(serialized_message['value'])
        # Increment the prometheus counter for processed values
        PROCESSED_VALUES_COUNT.inc()
        logger.info(f'Publish the sensor value to {processed_data_topic}')
        # Send the sensor value with the numer of the sensor extracted from the received topic sensor_data_topic_*
        await processed_data_topic.send(timestamp=stream.current_event.message.timestamp, key="sensor_value", value=json.dumps({'sensor_num':serialized_message['sensor_num'], 'value':serialized_message['value']}).encode())
        # Increment the prometheus counter for sent values
        SENT_VALUES_COUNT.inc()
        

@app.task
async def on_started() -> None:
    logger.info('Starting prometheus server to expose the metrics on port=7003')
    start_http_server(port=7003)
