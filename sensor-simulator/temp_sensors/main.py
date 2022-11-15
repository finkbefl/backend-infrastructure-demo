# Publish random temperature values between a range via paho mqtt python client
# Prerequisite is a running mqtt broker and paho-mqtt must be installed

import paho.mqtt.client as mqtt
import logging
import time
from threading import Thread
import random
import json
import datetime;

# Configure the logging mechanism
logging.basicConfig(
    # Default Level
    level = logging.INFO,
    # Formatting the logs
    format="%(asctime)s,%(msecs)d%(levelname)-8s[%(name)s:%(filename)s(%(lineno)d)]%(message)s")

# Get the logger
logger = logging.getLogger(__name__)

def main () :
    """
        Start of the python program.
        ----------
        Parameters :
        no parameters
        ----------
        Returns :
        no returns
    """
    logger.info ( " ########## START ########## " )

    ### IoT Sensors ###

    client = mqtt.Client("sensor1")
    client.on_connect = on_connect_sensor
    #client.username_pw_set(username="admin", password="admin")
    #client.connect("first-steps-mqtt-broker", 1883, 60) # mosquitto broker
    client.connect("kafka-mqtt-proxy", 1883, 60) # confluent proxy
    client.loop_start()

    try:
        logger.info ( "Simulating temp sensor 1: Publish to topic /sensor1/temp" )	
        new_thread = Thread(target=publishTemp,args=(client, "/sensor1/temp", 1))
        new_thread.start()
    except:
        logger.error("Error: unable to start thread for sensor 1")

def on_connect_sensor(mqttc, userdata, flags, rc):
    """
        The callback for when the client receives a CONNACK response from the server.
        ----------
        Parameters :
            mqttc:      The client instance
            userdata:   Private userdata
            flags:      Response flags sent by the broker
            rc:         The connection result (0: Connection successful)
        ----------
        Returns :
        no returns
    """
    logger.info(str(mqttc) + "Connected with result code" + str(rc))

def publishTemp(mqtt_client, topic, delay_time):
    """
        Publish a temperature value between 20 and 30 to a mqtt topic periodically
        ----------
        Parameters :
            mqtt-client:    The mqtt-client
            topic:          The topic to publish
            delay_time:     The time between two values
        ----------
        Returns :
        no returns
    """
    while 1:
        data = random.randint(20, 30)
        dataToSend = json.dumps({'timestamp': str((datetime.datetime.now().timestamp())),'topic': topic, 'value': str(data)})
        logger.info(dataToSend)
        mqtt_client.publish(topic, dataToSend, 0)
        time.sleep(delay_time)
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

# When this script is called directly ...
if __name__ == '__main__':
    # ... then calling the function main ()
    main ()