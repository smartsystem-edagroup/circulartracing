import paho.mqtt.client as mqtt
import time
import uuid
import json

#####IMPORTANT: RUN USING PYTHON3, DOES NOT WORK WITH PYTHON2 DUE TO THE FACT THAT PAHO MQTT ONLY SENDS STRINGS
#####			FOR SOME REASON, AND IN THIS EXAMPLE THERE IS THE NEED TO SEND A BYTEARRAY
##### IMPORTANT2: THE SLEEPS ARE NECESARY TO FIRSTLY CONNECT CORRECTLY TO THE BROKER, THEN TO WAIT THAT ALL THE DATA
##### 			  IS SENT BEFORE CLOSING THE CONNECTION
# Broker IP
HOST_NAME = 'circular.polito.it'
# client name
CLIENT_NAME = 'test'


def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt



if __name__ == '__main__':
    
    idclient = uuid.uuid1()
    client =mqtt.Client(CLIENT_NAME)
    client.on_connect = on_connect

    client.tls_set(ca_certs="/home/francovolante/Desktop/certs/ca.crt", certfile="/home/francovolante/Desktop/certs/client.crt", keyfile="/home/francovolante/Desktop/certs/client.key")	#absolute path to the certificate
    client.username_pw_set(username="sensor", password="sensor")
    client.tls_insecure_set(False)
    client.connect(HOST_NAME, port=8883)
	
    client.loop_start()
    msg = [ 137 , 133 , 130 , 124 , 138 , 134 , 132 ]
    jsonobj = {"bn" : idclient, "bt" : time.time(), "e" : {"n": "sensor", "u":"float", "v": msg}}

    time.sleep(1)
    
    result = client.publish("input/image/"+ str(idclient), json.dumps(jsonobj))
    msg_status = result[0]
    if msg_status == 0:
        print("Message sent correctly")
    else:
        print("Error in sending the message")
        
    time.sleep(2)
    client.loop_stop()
	

	
