# Collect all raw sensor-data from kafka

import logging
import json
import faust
from prometheus_client import Counter, start_http_server

SERVICE_NAME = "data_collection"

# Event counter for monitoring the received sensor values with prometheus
GET_SENSOR_DATA_COUNT = Counter("sensor_data_received", "The number of sensor-data values received trom sensor-data1 topic")

# Configure the logging mechanism
logging.basicConfig(
    # Default Level
    level = logging.INFO,
    # Formatting the logs
    format="%(asctime)s,%(msecs)d%(levelname)-8s[%(name)s:%(filename)s(%(lineno)d)]%(message)s")

# Get the logger
logger = logging.getLogger(__name__)

app = faust.App(SERVICE_NAME, broker="broker:29092", value_serializer='raw')
sensor_data_topic = app.topic("sensor-data1", partitions=8)


@app.agent(sensor_data_topic)
async def on_event(stream) -> None:
    async for msg_key, msg_value in stream.items():
        # At first imcrement the event counter for prometheus monitoring
        GET_SENSOR_DATA_COUNT.inc()
        logger.info(f'Received new pair message {msg_value}')
        serialized_message = json.loads(msg_value)
        for pair_name, pair_value in serialized_message.items():
            logger.info(f"Key: {msg_key} - Extracted pair: {pair_name}: {pair_value}")
            yield msg_value

@app.task
async def on_started() -> None:
    logger.info('Starting prometheus server to expose the metrics on port=7002')
    start_http_server(port=7002)
