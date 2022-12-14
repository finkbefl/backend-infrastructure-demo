# Load processed and aggregated data to the database

import logging
import datetime
import json
import faust
from database import Database
from prometheus_client import Counter, Histogram, start_http_server

SERVICE_NAME = "db_loader"

_INF = float("inf")

# Event counter for monitoring with prometheus
# The received sensor values
SENSOR_VALUES_COUNT = Counter("sensor_values_loaded", "The number of sensor-data values received from processed-data topic and loaded into db")
# The aggregated sensor values
AGGREGATED_VALUES_COUNT = Counter("aggregated_values_loaded", "The number of aggregated sensor-data values received from topic aggregated-data and loaded into db")
# Latency of received sensor values
SENSOR_VALUE_LATENCY = Histogram('sensor_value_latency', 'Cumulative histogram of latency in seconds of sensor values', buckets=(0.01, 0.02, 0.03, 0.04, 0.05, 0.1, _INF))
# Latency of received aggregated values
AGGREGATED_VALUE_LATENCY = Histogram('aggregated_value_latency', 'Cumulative histogram of latency in seconds of aggregated values', buckets=(0.01, 0.02, 0.03, 0.04, 0.05, 0.1, _INF))

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
        logger.info(f'Received new sensor value {msg_value}')
        serialized_message = json.loads(msg_value)
        # At first imcrement the event counter for prometheus monitoring of the received sensor values
        SENSOR_VALUES_COUNT.inc()
        # Load the temperature into the database
        await db.save_temperature(timestamp=float(stream.current_event.message.timestamp), sensor_num=int(serialized_message['sensor_num']), value=int(serialized_message['value']))
        # Calculate Latency and provide it to prometheus
        latency = datetime.datetime.now().timestamp() - float(stream.current_event.message.timestamp)
        logger.info(f"Calculated latency: {latency}")
        SENSOR_VALUE_LATENCY.observe(latency)

@app.agent(average_changelog_topic)
async def on_average_event(stream) -> None:
    async for msg_key, msg_value in stream.items():
        logger.info(f'Key: {msg_key} - Received new average value {msg_value}')
        serialized_message = json.loads(msg_value)
        # At first imcrement the event counter for prometheus monitoring of the received aggregated values
        AGGREGATED_VALUES_COUNT.inc()
        # Load the average into the database
        await db.save_average(timestamp=float(stream.current_event.message.timestamp), sensor_num=int(json.loads(msg_key)), value=float(serialized_message['average']))
        # Calculate Latency and provide it to prometheus
        latency = datetime.datetime.now().timestamp() - float(stream.current_event.message.timestamp)
        logger.info(f"Calculated latency: {latency}")
        AGGREGATED_VALUE_LATENCY.observe(latency)
        

@app.task
async def on_started() -> None:
    logger.info('Starting prometheus server to expose the metrics on port=7005')
    start_http_server(port=7005)
