import torch
import torchvision
import cv2
import time
from PIL import Image

import numpy as np
import random
import sys
import serial.tools.list_ports
from Adafruit_IO import MQTTClient
from ai import *

AIO_FEED_IDS =["led", "bbc-pump", "ai", "temp", "bbc-temp"]
AIO_USERNAME = "duy_ngotu"
AIO_KEY = "aio_YTrq60ESZzTgFii2z5P2vmZK8tDw"

model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
camera = cv2.VideoCapture(0)



while True:
    ret, image = camera.read()
    cv2.imshow('Webcam Image', image)
    result = model(image)
    print("detecting...")
    result.print()
    camera.release()