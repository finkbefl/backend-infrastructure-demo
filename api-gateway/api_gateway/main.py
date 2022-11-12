# Consumer REST API

import logging
from typing import List, Dict
import datetime
from fastapi import FastAPI
from database import Database
from prometheus_client import Counter, Histogram, start_http_server

_INF = float("inf")

# Event counter for monitoring with prometheus
# Number of sensor values requests
SENSOR_VALUES_COUNT = Counter("sensor_values_requests", "The number of sensor-data values requests via REST API")
# Number of aggregated values requests
AGGREGATED_VALUES_COUNT = Counter("aggregated_values_requests", "The number of aggregated values requests via REST API")
# Number of latest sensor value requests
LATEST_VALUE_COUNT = Counter("latest_value_requests", "The number of latest value requests via REST API")
# Age of latest sensor value request
LATEST_VALUE_AGE = Histogram('latest_value_requests_age_seconds', 'Cumulative histogram of age in seconds of latest value requests', buckets=(0.2, 0.4, 0.6, 0.8, 1, 1.2, _INF))


# Configure the logging mechanism
logging.basicConfig(
    # Default Level
    level = logging.INFO,
    # Formatting the logs
    format="%(asctime)s,%(msecs)d%(levelname)-8s[%(name)s:%(filename)s(%(lineno)d)]%(message)s")

# Get the logger
logger = logging.getLogger(__name__)

# Database Interface
db = Database()

# FastAPI

fastapi_app = FastAPI(title="REST API")

@fastapi_app.get("/temperature")
async def get_temperature_values(sensor_num: int, timestamp_start: float, timestamp_end: float) -> List[Dict]:
    logger.info("Get temperature values")
    SENSOR_VALUES_COUNT.inc()
    return await db.get_temperature_values(sensor_num, timestamp_start, timestamp_end)

@fastapi_app.get("/average")
async def get_average_values(sensor_num: int, timestamp_start: float, timestamp_end: float) -> List[Dict]:
    logger.info("Get average values")
    AGGREGATED_VALUES_COUNT.inc()
    return await db.get_average_values(sensor_num, timestamp_start, timestamp_end)

@fastapi_app.get("/temperature_latest")
async def get_temperature_latest(sensor_num: int) -> int:
    logger.info("Get latest temp")
    LATEST_VALUE_COUNT.inc()
    # Calc age in seconds
    received_data = await db.get_latest_temperature_value(sensor_num)
    # TODO Error handling (e.g. no data received)
    age = datetime.datetime.now().timestamp() - float(received_data[0]['timestamp'])
    logger.info(f"Calculated age of latest temp: {age}")
    LATEST_VALUE_AGE.observe(age)
    return received_data

@fastapi_app.on_event("startup")
async def startup_event():
    logger.info('Starting prometheus server to expose the metrics on port=7006')
    start_http_server(port=7006)