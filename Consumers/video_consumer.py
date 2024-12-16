import paho.mqtt.client as mqtt

import json
import time

CLIENT_NAME = 'IoT'
HOST_NAME = 'test.mosquitto.org'

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected to broker with result code {0}".format(str(rc)))  # Print result of connection attempt
	client.subscribe('/fvolante/output/video/#')
 
def on_message(client, userdata, message):
    print("Message received: ", json.loads(message.payload))
    time.sleep(1)
    
    
    
if __name__ == '__main__':
    client =mqtt.Client(CLIENT_NAME)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST_NAME, port=1883)
    time.sleep(1)
    client.loop_forever()