import numpy as np
import matplotlib.pyplot as plt
import tflite_runtime.interpreter as tflite
from zipfile import ZipFile
import time
import os
import paho.mqtt.client as mqtt
import json

# Client Name
CLIENT_NAME = 'IoT'
# Broker IP
HOST_NAME = 'circular.polito.it'
# Output host IP
OUTPUT_HOST_NAME = 'test.mosquitto.org'

#ogni riga è una misurazione di vari sensori
#prova è un array di array (matrice for short)
#per poterlo utilizzare, bisogna fare
#input2 = [input]
#valore_giusto = numpy.uint8(input2)
#valore_giusto ha al suo interno ciò che va dato in pasto a input_tensor
#la prediction è a 120 valori
#basta fare che legge fino a quando non arriva a 120 poi lancia la prediction con l'array creato
input =  [[ 132 , 146 , 144 , 132 , 154 , 121 , 120 ],
[ 132 , 143 , 140 , 126 , 154 , 123 , 119 ],
[ 132 , 142 , 139 , 126 , 153 , 124 , 121 ],
[ 132 , 141 , 137 , 124 , 151 , 125 , 119 ],
[ 131 , 140 , 136 , 124 , 149 , 126 , 119 ],
[ 131 , 138 , 134 , 123 , 147 , 128 , 116 ],
[ 131 , 137 , 133 , 122 , 145 , 129 , 117 ],
[ 131 , 135 , 132 , 122 , 143 , 130 , 116 ],
[ 131 , 135 , 132 , 122 , 143 , 130 , 118 ],
[ 131 , 136 , 132 , 122 , 144 , 130 , 120 ],
[ 131 , 137 , 133 , 121 , 146 , 129 , 125 ],
[ 132 , 138 , 135 , 122 , 149 , 127 , 125 ],
[ 132 , 146 , 144 , 123 , 164 , 120 , 123 ],
[ 131 , 150 , 149 , 139 , 156 , 117 , 129 ],
[ 130 , 155 , 157 , 151 , 157 , 113 , 134 ],
[ 130 , 155 , 158 , 153 , 156 , 112 , 126 ],
[ 130 , 155 , 157 , 149 , 159 , 113 , 117 ],
[ 130 , 155 , 157 , 147 , 161 , 113 , 121 ],
[ 130 , 153 , 155 , 143 , 162 , 114 , 122 ],
[ 130 , 153 , 154 , 143 , 160 , 114 , 127 ],
[ 131 , 152 , 152 , 138 , 163 , 115 , 125 ],
[ 131 , 150 , 150 , 135 , 161 , 116 , 123 ],
[ 131 , 149 , 148 , 133 , 161 , 118 , 121 ],
[ 131 , 148 , 147 , 132 , 160 , 119 , 121 ],
[ 131 , 147 , 145 , 130 , 159 , 119 , 128 ],
[ 131 , 146 , 144 , 129 , 158 , 120 , 130 ],
[ 131 , 146 , 144 , 128 , 158 , 120 , 120 ],
[ 131 , 146 , 144 , 129 , 157 , 120 , 124 ],
[ 131 , 145 , 143 , 128 , 157 , 121 , 119 ],
[ 130 , 145 , 143 , 128 , 156 , 121 , 121 ],
[ 130 , 144 , 142 , 127 , 155 , 122 , 127 ],
[ 130 , 144 , 141 , 127 , 155 , 122 , 123 ],
[ 130 , 144 , 141 , 126 , 155 , 122 , 124 ],
[ 131 , 144 , 141 , 126 , 155 , 122 , 121 ],
[ 131 , 147 , 145 , 130 , 158 , 120 , 123 ],
[ 131 , 148 , 146 , 133 , 157 , 119 , 132 ],
[ 131 , 152 , 153 , 141 , 161 , 115 , 140 ],
[ 130 , 155 , 157 , 145 , 164 , 112 , 140 ],
[ 129 , 157 , 161 , 150 , 165 , 110 , 147 ],
[ 129 , 158 , 164 , 155 , 164 , 109 , 142 ],
[ 129 , 157 , 161 , 149 , 166 , 110 , 145 ],
[ 128 , 153 , 155 , 134 , 173 , 113 , 145 ],
[ 129 , 151 , 151 , 133 , 166 , 115 , 138 ],
[ 129 , 152 , 152 , 133 , 168 , 115 , 130 ],
[ 130 , 148 , 147 , 127 , 166 , 118 , 119 ],
[ 131 , 147 , 146 , 126 , 165 , 119 , 123 ],
[ 132 , 147 , 145 , 125 , 165 , 119 , 120 ],
[ 132 , 146 , 144 , 124 , 164 , 120 , 128 ],
[ 132 , 146 , 144 , 124 , 163 , 120 , 128 ],
[ 132 , 145 , 142 , 123 , 161 , 121 , 117 ],
[ 132 , 144 , 141 , 123 , 159 , 122 , 120 ],
[ 132 , 143 , 140 , 122 , 159 , 123 , 117 ],
[ 132 , 143 , 140 , 122 , 158 , 124 , 120 ],
[ 132 , 142 , 139 , 122 , 158 , 124 , 117 ],
[ 132 , 142 , 138 , 122 , 156 , 124 , 121 ],
[ 132 , 142 , 138 , 121 , 156 , 124 , 118 ],
[ 132 , 141 , 138 , 121 , 155 , 125 , 120 ],
[ 132 , 141 , 138 , 121 , 155 , 125 , 123 ],
[ 132 , 141 , 138 , 121 , 155 , 125 , 120 ],
[ 132 , 145 , 143 , 123 , 162 , 121 , 122 ],
[ 132 , 150 , 149 , 123 , 175 , 116 , 120 ],
[ 131 , 155 , 158 , 140 , 170 , 112 , 128 ],
[ 132 , 153 , 154 , 134 , 171 , 114 , 121 ],
[ 131 , 154 , 156 , 135 , 172 , 113 , 119 ],
[ 131 , 150 , 150 , 125 , 172 , 116 , 122 ],
[ 131 , 148 , 147 , 127 , 166 , 118 , 139 ],
[ 131 , 148 , 147 , 125 , 168 , 118 , 117 ],
[ 131 , 148 , 146 , 130 , 160 , 119 , 139 ],
[ 131 , 145 , 143 , 127 , 157 , 121 , 133 ],
[ 131 , 145 , 142 , 127 , 157 , 122 , 121 ],
[ 132 , 143 , 140 , 124 , 156 , 123 , 124 ],
[ 132 , 143 , 139 , 123 , 156 , 124 , 120 ],
[ 132 , 141 , 138 , 123 , 153 , 125 , 126 ],
[ 133 , 141 , 137 , 122 , 153 , 126 , 125 ],
[ 132 , 140 , 137 , 122 , 152 , 126 , 124 ],
[ 132 , 140 , 137 , 122 , 153 , 126 , 120 ],
[ 132 , 140 , 136 , 122 , 152 , 126 , 120 ],
[ 131 , 140 , 136 , 122 , 152 , 126 , 122 ],
[ 130 , 139 , 135 , 122 , 150 , 127 , 121 ],
[ 130 , 138 , 135 , 121 , 150 , 127 , 124 ],
[ 130 , 138 , 134 , 121 , 148 , 128 , 120 ],
[ 130 , 138 , 135 , 121 , 149 , 127 , 122 ],
[ 130 , 140 , 137 , 121 , 153 , 125 , 118 ],
[ 131 , 144 , 141 , 121 , 161 , 122 , 126 ],
[ 131 , 145 , 142 , 122 , 162 , 121 , 136 ],
[ 131 , 145 , 143 , 127 , 159 , 121 , 127 ],
[ 130 , 147 , 145 , 130 , 160 , 119 , 124 ],
[ 130 , 148 , 147 , 133 , 158 , 118 , 121 ],
[ 129 , 146 , 144 , 128 , 159 , 119 , 128 ],
[ 128 , 147 , 146 , 131 , 159 , 118 , 126 ],
[ 129 , 143 , 140 , 126 , 154 , 123 , 126 ],
[ 130 , 141 , 138 , 124 , 152 , 124 , 124 ],
[ 131 , 141 , 137 , 124 , 151 , 125 , 133 ],
[ 131 , 141 , 138 , 124 , 152 , 125 , 133 ],
[ 132 , 141 , 137 , 125 , 151 , 125 , 141 ],
[ 132 , 140 , 136 , 125 , 149 , 126 , 137 ],
[ 133 , 139 , 136 , 125 , 147 , 127 , 140 ],
[ 133 , 138 , 135 , 126 , 144 , 128 , 146 ],
[ 134 , 137 , 133 , 125 , 143 , 129 , 142 ],
[ 133 , 136 , 133 , 125 , 141 , 130 , 144 ],
[ 133 , 137 , 133 , 126 , 142 , 130 , 146 ],
[ 133 , 136 , 133 , 124 , 143 , 130 , 136 ],
[ 133 , 136 , 133 , 125 , 142 , 130 , 140 ],
[ 133 , 136 , 132 , 124 , 141 , 130 , 133 ],
[ 133 , 135 , 132 , 125 , 141 , 131 , 136 ],
[ 133 , 136 , 132 , 125 , 140 , 131 , 137 ],
[ 133 , 136 , 133 , 126 , 140 , 130 , 135 ],
[ 132 , 136 , 133 , 127 , 139 , 130 , 138 ],
[ 132 , 138 , 134 , 130 , 139 , 129 , 132 ],
[ 131 , 140 , 136 , 133 , 139 , 126 , 152 ],
[ 130 , 139 , 135 , 132 , 138 , 127 , 153 ],
[ 132 , 132 , 128 , 125 , 134 , 134 , 124 ],
[ 131 , 134 , 130 , 126 , 136 , 132 , 128 ],
[ 132 , 135 , 132 , 129 , 135 , 131 , 142 ],
[ 132 , 136 , 133 , 130 , 136 , 130 , 129 ],
[ 133 , 137 , 133 , 132 , 135 , 130 , 136 ],
[ 134 , 136 , 132 , 131 , 135 , 131 , 133 ],
[ 136 , 134 , 130 , 125 , 137 , 133 , 122 ],
[ 137 , 133 , 130 , 124 , 138 , 134 , 132 ]]


clients = []

interpreter = tflite.Interpreter('weather_forecast_quant.tflite', experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')])
interpreter.allocate_tensors()

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected to broker with result code {0}".format(str(rc)))  # Print result of connection attempt
	client.subscribe('sensor/#')

def on_connect_resp(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected to broker with result code {0}".format(str(rc)))

def on_message(client, userdata, message):
    print("Message received.")
    obj = json.loads(message.payload)
    topic = message.topic
    if(len(input)==120):
      input.pop(0)
    input.append(obj["e"]["v"])
    if (len(input) == 120):
      topredict = np.uint8([input])
      prediction = predict_weather(interpreter, topredict)
      ret_client =mqtt.Client(CLIENT_NAME)
      ret_client.on_connect = on_connect_resp
      ret_client.connect(OUTPUT_HOST_NAME, port=1883)
      ret_client.loop_start()
      tosend = {"bn" : obj["bn"], "bt" : time.time(), "e" : {"n": "prediction", "u":"float", "v": prediction[0]}}
      ret_client.publish("/fvolante/output/" + topic, json.dumps(tosend))
      ret_client.loop_stop()
      ret_client.disconnect()
      
    time.sleep(1)
    print("Done")

def set_input_tensor(interpreter, input):
  input_details = interpreter.get_input_details()[0]
  tensor_index = input_details['index']
  input_tensor = interpreter.tensor(tensor_index)()
  # Inputs for the TFLite model must be uint8, so we quantize our input data.
  scale, zero_point = input_details['quantization']
  #quantized_input = np.uint8(input / scale + zero_point) #gli input forniti sono già quantizzati
  input_tensor[:, :, :] = input

def predict_weather(interpreter, input):
  set_input_tensor(interpreter, input)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = interpreter.get_tensor(output_details['index'])
  # Outputs from the TFLite model are uint8, so we dequantize the results:
  scale, zero_point = output_details['quantization']
  output = scale * (output - zero_point)
  return output



def main():
  mqttClient = mqtt.Client(CLIENT_NAME)
  mqttClient.on_connect = on_connect
  mqttClient.on_message = on_message
  mqttClient.tls_set(ca_certs="/home/francovolante/Desktop/certs/ca.crt", certfile="/home/fvolante/server.crt", keyfile="/home/fvolante/server.key")	#absolute path to the certificate
  mqttClient.username_pw_set(username="gateway", password="gateway")
  mqttClient.tls_insecure_set(False)
  mqttClient.connect(HOST_NAME, port=8883)
  mqttClient.loop_forever()


if __name__ == "__main__":
    main()


