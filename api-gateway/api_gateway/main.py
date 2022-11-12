# Consumer REST API

import logging
from typing import List, Dict
from fastapi import FastAPI
from database import Database
from prometheus_client import Counter, Histogram, start_http_server

# Event counter for monitoring with prometheus
# Number of sensor values requests
SENSOR_VALUES_COUNT = Counter("sensor_values_requests", "The number of sensor-data values requests via REST API")
# Number of aggregated values requests
AGGREGATED_VALUES_COUNT = Counter("aggregated_values_requests", "The number of aggregated values requests via REST API")
# Number of latest sensor value requests
LATEST_VALUE_COUNT = Counter("latest_value_requests", "The number of latest value requests via REST API")


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

@fastapi_app.get("/temperature_realtime")
async def get_temperature_realtime(sensor_num: int) -> int:
    logger.info("Get latest realtime temp")
    LATEST_VALUE_COUNT.inc()
    return await db.get_latest_temperature_value(sensor_num)

@fastapi_app.on_event("startup")
async def startup_event():
    logger.info('Starting prometheus server to expose the metrics on port=7006')
    start_http_server(port=7006)