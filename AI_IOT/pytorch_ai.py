import torch
import torchvision
import cv2
import time
from PIL import Image
import numpy as np


# Assigning the Device which will do the calculation
device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
print("cuda = ",torch.cuda.is_available())
model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
# model = model.to(device)
camera = cv2.VideoCapture(0)



def image_detector2():
    ret, image = camera.read()
    # image = cv2.resize(image, (720, 720), interpolation=cv2.INTER_AREA)

    # Show the image in a window
    # cv2.imshow('Webcam Image', image)
    result = model(image)
    print("detecting...")
    print(torch.cuda.is_available())
    result.print()
    camera.release()
    return result


