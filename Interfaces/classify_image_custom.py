# Lint as: python3
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""Example using PyCoral to classify a given image using an Edge TPU.

To run this code, you must attach an Edge TPU attached to the host and
install the Edge TPU runtime (`libedgetpu.so`) and `tflite_runtime`. For
device setup instructions, see coral.ai/docs/setup.

Example usage:
```
bash examples/install_requirements.sh classify_image.py

python3 examples/classify_image.py \
  --model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite  \
  --labels test_data/inat_bird_labels.txt \
  --input test_data/parrot.jpg
```
"""

import argparse
import time
import io
import json

import numpy as np
from PIL import Image
from pycoral.adapters import classify
from pycoral.adapters import common
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

def mqtt_classify(bytearray):
    labels = read_label_file("test_data/inat_bird_labels.txt")
    interpreter = make_interpreter("test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite")
    interpreter.allocate_tensors()

    # Model must be uint8 quantized
    if common.input_details(interpreter, 'dtype') != np.uint8:
        raise ValueError('Only support uint8 input type.')
    
    size = common.input_size(interpreter)
    image = Image.open(io.BytesIO(bytearray)).convert('RGB').resize(size, Image.ANTIALIAS)
    
    
    
  # Image data must go through two transforms before running inference:
  # 1. normalization: f = (input - mean) / std
  # 2. quantization: q = f / scale + zero_point
  # The following code combines the two steps as such:
  # q = (input - mean) / (std * scale) + zero_point
  # However, if std * scale equals 1, and mean - zero_point equals 0, the input
  # does not need any preprocessing (but in practice, even if the results are
  # very close to 1 and 0, it is probably okay to skip preprocessing for better
  # efficiency; we use 1e-5 below instead of absolute zero).
    params = common.input_details(interpreter, 'quantization_parameters')
    scale = params['scales']
    zero_point = params['zero_points']
    mean = 128.0
    std = 128.0
    if abs(scale * std - 1) < 1e-5 and abs(mean - zero_point) < 1e-5:
    # Input data does not require preprocessing.
        common.set_input(interpreter, image)
    else:
    # Input data requires preprocessing
        normalized_input = (np.asarray(image) - mean) / (std * scale) + zero_point
        np.clip(normalized_input, 0, 255, out=normalized_input)
        common.set_input(interpreter, normalized_input.astype(np.uint8))
    # Run inference
    print('----INFERENCE TIME----')
    print('Note: The first inference on Edge TPU is slow because it includes',
        'loading the model into Edge TPU memory.')
    for _ in range(5):
        start = time.perf_counter()
        interpreter.invoke()
        inference_time = time.perf_counter() - start
        classes = classify.get_classes(interpreter, 1, 0.0)
        print('%.1fms' % (inference_time * 1000))

    print('-------RESULTS--------')
    output = {"bn" : [], "bt" : time.time(), "e" : []}

    ##invece di fare questa print, ritornare o una stringa o i dati necessari per creare un json da rispedire con mqtt
    for c in classes:
        output["e"].append({"n" : labels.get(c.id,c.id), "u":"result","v":c.score})
        #print('%s: %.5f' % (labels.get(c.id, c.id), c.score))
        #outstring = "%s: %.5f" % (labels.get(c.id,c.id), c.score)
    return output