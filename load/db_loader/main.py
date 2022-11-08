# Load processed and aggregated data to the database

import logging
import json
import faust
from database import Database
from prometheus_client import Counter, start_http_server

SERVICE_NAME = "db_loader"

# Event counter for monitoring with prometheus
# The received sensor values
SENSOR_VALUES_COUNT = Counter("sensor_values_loaded", "The number of sensor-data values received from processed-data topic and loaded into db")
# The aggregated sensor values
AGGREGATED_VALUES_COUNT = Counter("aggregated_values_loaded", "The number of aggregated sensor-data values received from topic aggregated-data and loaded into db")

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
average_changelog_topic = app.topic("data_aggregation-average-changelog", partitions=8)

# Database Interface
db = Database()

@app.agent(processed_data_topic)
async def on_event(stream) -> None:
    async for msg_key, msg_value in stream.items():
        logger.info(f'Key: {msg_key} - Received new sensor value {msg_value}')
        serialized_message = json.loads(msg_value)
        # At first imcrement the event counter for prometheus monitoring of the received sensor values
        SENSOR_VALUES_COUNT.inc()
        # Load the temperature into the database
        await db.save_temperature(timestamp=float(stream.current_event.message.timestamp), sensor_num=int(serialized_message['sensor_num']), value=int(serialized_message['value']))

@app.agent(average_changelog_topic)
async def on_average_event(stream) -> None:
    async for msg_key, msg_value in stream.items():
        logger.info(f'Key: {msg_key} - Received new average value {msg_value}')
        serialized_message = json.loads(msg_value)
        # At first imcrement the event counter for prometheus monitoring of the received aggregated values
        AGGREGATED_VALUES_COUNT.inc()
        # Load the average into the database
        await db.save_average(timestamp=float(stream.current_event.message.timestamp), sensor_num=int(json.loads(msg_key)), value=float(serialized_message['average']))
        

@app.task
async def on_started() -> None:
    logger.info('Starting prometheus server to expose the metrics on port=7005')
    start_http_server(port=7005)
