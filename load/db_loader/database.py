# The Postgres Database Interface

import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from data_definition import Temperature, Average
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

# Database Params TODO: Make it configurable and credentials must not in source code
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
        save_temperature : Save a temperature value into the database
        save_average : Save a temperature average value into the database
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

    async def save_temperature(self, timestamp: float, sensor_num: int, value: int) -> None:
        """
        Save a temperature value into the database
        ----------
        Parameters:
            timestamp : float
                The timestamp of the temperature value
            sensor_num : int
                Number of the sensor
            value : int
                The temperature value
        ----------
        Returns:
            no returns
        """
        async with AsyncSession(self.db_engine) as session:
            async with session.begin():
                logger.info(f"Save sensor value for sensor num {sensor_num}: {value}")
                temperature = Temperature(timestamp=timestamp, sensor_num=sensor_num, value=value)
                session.add(temperature)

    async def save_average(self, timestamp: float, sensor_num: int, value: float) -> None:
        """
        Save a temperature average value into the database
        ----------
        Parameters:
            timestamp : float
                The timestamp of the average value
            sensor_num : int
                Number of the sensor
            value : float
                The average value
        ----------
        Returns:
            no returns
        """
        async with AsyncSession(self.db_engine) as session:
            async with session.begin():
                selected_average_execution = await session.execute(
                    select(Average).filter(Average.sensor_num == sensor_num))
                selected_average = selected_average_execution.scalars().first()
                if selected_average:
                    logger.info(f"Update existing average {sensor_num}: {value}")
                    selected_average.value = value
                else:
                    logger.info(f"Save average {sensor_num}: {value}")
                    average = Average(timestamp=timestamp, sensor_num=sensor_num, value=value)
                    session.add(average)


async def async_main():
    # Create database engine object with a "connection string"
    engine = create_async_engine(
        con_str,
        echo=False, # Not print outputs
    )
    # When starting the Database Container initially drop all data and create the tables
    async with engine.begin() as conn:
        await conn.run_sync(Temperature.metadata.drop_all)
        await conn.run_sync(Average.metadata.drop_all)

        await conn.run_sync(Temperature.metadata.create_all)
        await conn.run_sync(Average.metadata.create_all)

# When this script is called directly ...
if __name__ == '__main__':
    # ... then initialize the database (during the startup of the container this script is called directly)
    asyncio.run(async_main())
