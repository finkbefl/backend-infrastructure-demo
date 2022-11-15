# The Postgres Database Interface for the API Gateway

import logging
from typing import List, Dict
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from data_definition import Temperature, Average
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

# Database Params TODO: Make it configurable and credentials not in source code
database_container_name = "database"
database_port = 5432
database_user = "postgres"
database_password = "postgres"
database_name = "temperature"
# Database connection string for postgresql server and asyncpg client interface
con_str = "postgresql+asyncpg://" + database_user + ":" + database_password + "@" + database_container_name+ ":" + str(database_port) + "/" + database_name

class Database():
    """
    A class as interface to the postgres database

    ----------
    Methods:
        get_latest_temperature_value : Get latest temperature value from the database
        get_temperature_values : Get temperature values from the database
        get_average_values : Get average values from the database
    """
    # Constructor Method
    def __init__(self):
        self.db_engine = self.__create_engine()

    def __create_engine(self) -> AsyncEngine:
        # Create database engine object with a "connection string"
        engine = create_async_engine(
            con_str,
            echo=False, # Not print outputs
        )
        return engine

    # Converting rows to dictionary
    def __row_to_dict(self, row) -> Dict:
        d = {}
        for column in row.__table__.columns:
            d[column.name] = str(getattr(row, column.name))
        return d

    async def get_latest_temperature_value(self, sensor_num: int) -> List[Dict]:
        """
        Get latest temperature value from the database
        ----------
        Parameters:
            sensor_num : int
                Number of the sensor
        ----------
        Returns:
            The latest temperature value : List[Dict]
        """
        async with AsyncSession(self.db_engine) as session:
            async with session.begin():
                logger.info(f"Get latest sensor value for sensor num {sensor_num}")
                selected_values_execution = await session.execute(
                    select(Temperature).filter(Temperature.sensor_num == sensor_num).order_by(Temperature.id.desc()).limit(1))
                selected_values = selected_values_execution.scalars().all()
                ret_data = [self.__row_to_dict(i) for i in selected_values]
                return ret_data

    async def get_temperature_values(self, sensor_num: int, timestamp_start: float, timestamp_end: float) -> List[Dict]:
        """
        Get temperature values from the database
        ----------
        Parameters:
            sensor_num : int
                Number of the sensor
            timestamp_start : float
                Return temperature values starting with this timestamp
            timestamp_end : float
                Return temperature values up to this timestamp
        ----------
        Returns:
            The temperature values : List[Dict]
        """
        async with AsyncSession(self.db_engine) as session:
            async with session.begin():
                logger.info(f"Get sensor values between timestamp range {timestamp_start} - {timestamp_end} for sensor num {sensor_num}")
                selected_values_execution = await session.execute(
                    select(Temperature).filter(Temperature.sensor_num == sensor_num).where((Temperature.timestamp >= timestamp_start) & (Temperature.timestamp <= timestamp_end)))
                selected_values = selected_values_execution.scalars().all()
                ret_data = [self.__row_to_dict(i) for i in selected_values]
                return ret_data

    async def get_average_values(self, sensor_num: int, timestamp_start: float, timestamp_end: float) -> List[Dict]:
        """
        Get average values from the database
        ----------
        Parameters:
            sensor_num : int
                Number of the sensor
            timestamp_start : float
                Return average values starting with this timestamp
            timestamp_end : float
                Return average values up to this timestamp
        ----------
        Returns:
            The average values : List[Dict]
        """
        async with AsyncSession(self.db_engine) as session:
            async with session.begin():
                logger.info(f"Get average values between timestamp range {timestamp_start} - {timestamp_end} for sensor num {sensor_num}")
                selected_values_execution = await session.execute(
                    select(Average).filter(Temperature.sensor_num == sensor_num).where((Temperature.timestamp >= timestamp_start) & (Temperature.timestamp <= timestamp_end)))
                selected_values = selected_values_execution.scalars().all()
                ret_data = [self.__row_to_dict(i) for i in selected_values]
                return ret_data