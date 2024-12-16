import paho.mqtt.client as mqtt

import json
import time
import classify_image_custom as image_classify
import uuid

# Client Name
CLIENT_NAME = 'IoT'
# Broker IP
HOST_NAME = 'circular.polito.it'
# Output host IP
OUTPUT_HOST_NAME = 'test.mosquitto.org'

#clients = []

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected to broker with result code {0}".format(str(rc)))  # Print result of connection attempt
	client.subscribe('image/#')

def on_connect_resp(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected to broker with result code {0}".format(str(rc)))

def on_message(client, userdata, message):
    print("Message received.")
    topic = message.topic
    messagejson = json.loads(message.payload)
    output = image_classify.mqtt_classify(messagejson['e']['v'])
    output["bn"].append(messagejson["bn"])
    ret_client = mqtt.Client(CLIENT_NAME)
    ret_client.on_connect = on_connect_resp
    ret_client.connect(OUTPUT_HOST_NAME,port=1883)
    ret_client.loop_start()
    ret_client.publish("fvolante/output/" + topic, json.dumps(output))
    ret_client.loop_stop()
    ret_client.disconnect()
    print("Done publishing ")
    
	


if __name__ == '__main__':

	mqttClient = mqtt.Client(CLIENT_NAME)
	mqttClient.on_connect = on_connect
	mqttClient.on_message = on_message
	mqttClient.tls_set(ca_certs="/home/fvolante/ca.crt", certfile="/home/fvolante/server.crt", keyfile="/home/fvolante/server.key")	#absolute path to the certificate
	mqttClient.username_pw_set(username="gateway", password="gateway")
	mqttClient.tls_insecure_set(False)
	mqttClient.connect(HOST_NAME, port=8883)
	mqttClient.loop_forever()
	# ret_client =mqtt.Client(CLIENT_NAME)
	# ret_client.on_connect = on_connect_resp
	# ret_client.connect(OUTPUT_HOST_NAME, port=1883)
	# clients.append(mqttClient)
	# clients.append(ret_client)
	# while(True):
	# 	for client in clients:
	# 		client.loop(3)
		

	
	

