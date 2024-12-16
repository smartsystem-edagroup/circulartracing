import cv2
import os
import time
import uuid
import paho.mqtt.client as mqtt
import json

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference
username = 'USERNAME'
password = 'PASSWORD'
endpoint = 'ENDPOINT'
ip = 'IPADDRESS'
CLIENT_NAME = 'test'
HOST_NAME = 'test.mosquitto.org'

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected to broker with result code {0}".format(str(rc)))  # Print result of connection attempt

def video_classify():
    interpreter = make_interpreter("test_data/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu")
    interpreter.allocate_tensors()
    labels = read_label_file("test_data/coco_labels.txt")
    inference_size = input_size(interpreter)
    cap = cv2.VideoCapture(f'rtsp://{username}:{password}@{ip}/{endpoint}')
    idclient = uuid.uuid1()
    client =mqtt.Client(CLIENT_NAME)
    client.on_connect = on_connect

    client.tls_set(ca_certs="/home/franco/Desktop/mqtt/certs/ca.crt")	#absolute path to the certificate
    client.tls_insecure_set(False)
    client.connect(HOST_NAME, port=1883)
	
    client.loop_start()
    time.sleep(1)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2_im = frame

        cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        cv2_im_rgb = cv2.resize(cv2_im_rgb, inference_size)
        run_inference(interpreter, cv2_im_rgb.tobytes())
        objs = get_objects(interpreter, 0.1)[:3]
        cv2_im = append_objs_to_img(cv2_im, inference_size, objs, labels)

        ### dentro cv2_im a questo punto c'è l'immagine con i bound identificati, che a questo punto deve essere inviata come risposta per mqtt
        msg = bytearray(cv2_im)
        jsonobj = {"bn" : idclient, "bt" : time.time(), "e" : {"n": "image", "u":"bytearray", "v": msg}}

        result = client.publish("fvolante/video/output/"+ str(idclient), json.dumps(jsonobj))
        
        msg_status = result[0]
        if msg_status == 0:
            print("Message sent correctly")
        else:
         print("Error in sending the message")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    client.loop_stop()
    cap.release()
    cv2.destroyAllWindows()

def append_objs_to_img(cv2_im, inference_size, objs, labels):
    height, width, channels = cv2_im.shape
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]
    for obj in objs:
        bbox = obj.bbox.scale(scale_x, scale_y)
        x0, y0 = int(bbox.xmin), int(bbox.ymin)
        x1, y1 = int(bbox.xmax), int(bbox.ymax)

        percent = int(100 * obj.score)
        label = '{}% {}'.format(percent, labels.get(obj.id, obj.id))

        cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2_im = cv2.putText(cv2_im, label, (x0, y0+30),
                             cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
    return cv2_im