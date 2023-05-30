import cv2
import torch
from time import time, sleep


model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')

dev_port = 0
non_working_ports = []
camPorts = []

while len(non_working_ports) < 3:  # if there are more than 4 non working ports stop the testing.
    camera = cv2.VideoCapture(dev_port)
    if not camera.isOpened():
        non_working_ports.append(dev_port)
        print("Port %s is not working." % dev_port)
    else:
        is_reading, img = camera.read()
        w = camera.get(3)
        h = camera.get(4)
        if is_reading:
            print("Port %s is working and reads images (%s x %s)" % (dev_port, h, w))
            camPorts.append(dev_port)
            camera.release()
        else:
            print("Port %s for camera ( %s x %s) is present but does not reads." % (dev_port, h, w))
    dev_port += 1


camera = cv2.VideoCapture(camPorts[0])

if not camera.isOpened():
    print("Cannot open camera")
    exit()

while True:

    start_time = time()
    is_reading, frame = camera.read()
    if not is_reading:
        print('cannot read frame at cam', camera)

    cv2.imshow('Tesing cam', frame)
    if cv2.waitKey(1) == ord('q'):
        break


    res = model(frame)
    res.print()
    # Data
    print('\n', res.xyxy[0])  # print img1 predictions

    result = str(res)
    print('Time take to read camera: ', str(time() - start_time))


camera.release()
cv2.destroyAllWindows()