# Collect all raw sensor-data from kafka

import logging
import json
import faust
from prometheus_client import Counter, start_http_server

SERVICE_NAME = "data_collection"

# Event counter for monitoring with prometheus
# The received sensor values
SENSOR_VALUES_COUNT = Counter("sensor_values_received", "The number of sensor-data values received trom sensor-data1 topic")
# The collected sensor values
COLLECTED_VALUES_COUNT = Counter("sensor_values_collected", "The number of sensor-data values collected")
# The sent sensor values
SENT_VALUES_COUNT = Counter("sensor_values_sent", "The number of sensor-data values sent to src-data topic")

# Configure the logging mechanism
logging.basicConfig(
    # Default Level
    level = logging.INFO,
    # Formatting the logs
    format="%(asctime)s,%(msecs)d%(levelname)-8s[%(name)s:%(filename)s(%(lineno)d)]%(message)s")

# Get the logger
logger = logging.getLogger(__name__)

app = faust.App(SERVICE_NAME, broker="broker:29092", value_serializer='raw')
sensor_data_topic_1 = app.topic("sensor-data1", partitions=8)
sensor_data_topic_2 = app.topic("sensor-data2", partitions=8)
src_data_topic = app.topic("src-data", partitions=8)



@app.agent(sensor_data_topic_1)
async def on_sensor_1_event(stream) -> None:
    # Create additional topics
    await sensor_data_topic_1.declare()
    await src_data_topic.declare()
    async for msg_key, msg_value in stream.items():
        # At first imcrement the event counter for prometheus monitoring of the received sensor values
        SENSOR_VALUES_COUNT.inc()
        logger.info(f'Received new sensor 1 value {msg_value}')
        serialized_message = json.loads(msg_value)
        # Increment the prometheus counter for collected values
        COLLECTED_VALUES_COUNT.inc()
        logger.info(f'Publish the sensor 1 value to {src_data_topic}')
        # Send the sensor value with the numer of the sensor extracted from the received topic sensor_data_topic_*
        await src_data_topic.send(timestamp=float(serialized_message['timestamp']), key="sensor_value", value=json.dumps({'sensor_num':''.join(filter(lambda i: i.isdigit(), str(msg_key))), 'value':serialized_message['value']}).encode())
        # Increment the prometheus counter for sent values
        SENT_VALUES_COUNT.inc()

@app.agent(sensor_data_topic_2)
async def on_sensor_2_event(stream) -> None:
    # Create additional topics
    await sensor_data_topic_2.declare()
    await src_data_topic.declare()
    async for msg_key, msg_value in stream.items():
        # At first imcrement the event counter for prometheus monitoring of the received sensor values
        SENSOR_VALUES_COUNT.inc()
        logger.info(f'Received new sensor 2 value {msg_value}')
        serialized_message = json.loads(msg_value)
        # Increment the prometheus counter for collected values
        COLLECTED_VALUES_COUNT.inc()
        logger.info(f'Publish the sensor 2 value to {src_data_topic}')
        # Send the sensor value with the numer of the sensor extracted from the received topic sensor_data_topic_*
        await src_data_topic.send(timestamp=float(serialized_message['timestamp']), key="sensor_value", value=json.dumps({'sensor_num':''.join(filter(lambda i: i.isdigit(), str(msg_key))), 'value':serialized_message['value']}).encode())
        # Increment the prometheus counter for sent values
        SENT_VALUES_COUNT.inc()
        

@app.task
async def on_started() -> None:
    logger.info('Starting prometheus server to expose the metrics on port=7002')
    start_http_server(port=7002)
