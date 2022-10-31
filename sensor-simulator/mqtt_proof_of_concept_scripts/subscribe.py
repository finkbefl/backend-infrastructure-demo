# Script to test mqtt subscribing via paho mqtt python client
# Prerequisite is a running mqtt broker and paho-mqtt must be installed

import paho.mqtt.client as mqtt
import logging
import json
from datetime import datetime 

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
	
	# Subscriber	
    clientSub = mqtt.Client("Subscriber")
    clientSub.on_connect = on_connect
    clientSub.on_message = on_message
    #clientSub.username_pw_set(username="admin", password="admin")
    clientSub.connect("localhost", 1883, 60)
    clientSub.loop_forever()
    #clientSub.loop_stop()

def on_connect(mqttc, userdata, flags, rc):
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
	# Subscribe with single-level-wildcard +
	# Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
	mqttc.subscribe("/+/temp")
	logger.info("Subscribe for /+/temp topics")
	
def on_message(client, userdata, msg):
	"""
		The callback for when the client receives a message for a topic.
		----------
		Parameters :
			client:     The client instance
			userdata:   Private userdata
			flags:      Response flags sent by the broker
			msg:        Instance of MQTTMessage
		----------
		Returns :
		no returns
    """
	payload = json.loads(msg.payload)
	date_time = datetime.fromtimestamp(float(payload['timestamp']))
	value = payload['value']
	logger.info(str(date_time) + " " + msg.topic + " value: " + value)

# When this script is called directly ...
if __name__ == '__main__':
    # ... then calling the function main ()
    main ()