# Collect all raw sensor-data from kafka

import logging
import json
import faust

SERVICE_NAME = "data_collection"

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
        logger.info(f'Received new pair message {msg_value}')
        serialized_message = json.loads(msg_value)
        for pair_name, pair_value in serialized_message.items():
            logger.info(f"Key: {msg_key} - Extracted pair: {pair_name}: {pair_value}")
            yield msg_value
