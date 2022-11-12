# Definitions of the database table structures as different classes
# Use the declerative mapping style to describe the database structure

# TODO: Not implement twice (db_loader and api_gateway)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float

# The Base Class
# ( column definitions within a class derived from this base class )
Base = declarative_base ()

# Classes which represent the table structure
# For the processed sensor values
class Temperature(Base):
    """
    A class to define the table structure for temperature values
    ----------
    Attributes:
        __tablename__ : str
            The name of the database table
        id : Integer
            The index of the data row
        timestamp : Float
            The timestamp of the sensor value
        sensor_num : Integer
            The number of the sensor
        value : Integer
            The temperature value
    ----------
    Methods:
        no methods
    """
    __tablename__ = "temperature"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    sensor_num = Column(Integer)
    value = Column(Integer)

# For the average values
class Average(Base):
    """
    A class to define the table structure for average values
    ----------
    Attributes:
        __tablename__ : str
            The name of the database table
        id : Integer
            The index of the data row
        timestamp : Float
            The timestamp of the average value
        sensor_num : Integer
            The number of the sensor
        value : Float
            The average value
    ----------
    Methods:
        no methods
    """
    __tablename__ = "average"
    id = Column(Integer, primary_key=True)
    timestamp = Column(Float)
    sensor_num = Column(Integer)
    value = Column(Float)

