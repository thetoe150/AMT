import torch
import torchvision
import cv2
import time
from PIL import Image
import numpy as np
#Assigning the Device which will do the calculation
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
model  = model.to(device)
camera = cv2.VideoCapture(0)

def image_detector2():
    im = Image.open('fire.jpg')
    ret, image = camera.read()
    cv2.imshow('img', image)
    # Resize the raw image into (224-height,224-width) pixels.
    #image = cv2.resize(image, (720, 720), interpolation=cv2.INTER_AREA)

    # Show the image in a window
    # cv2.imshow('Webcam Image', image)
    # Make the image a numpy array and reshape it to the models input shape.
    #image = np.asarray(image, dtype=np.float32).reshape(1, 720, 720, 3)
    # Normalize the image array
    #image = (image / 127.5) - 1
    result = model(image)
    print("detecting...")
    result.print()
    #return result
    return result
while(True):
    image_detector2()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
camera.release()