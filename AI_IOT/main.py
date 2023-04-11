import cv2
import torch
import time
import serial.tools.list_ports
import platform
import IOT
import physical

if __name__ == "__main__":
    print("Hello, World!")

def list_ports():
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []
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
                working_ports.append(dev_port)
            else:
                print("Port %s for camera ( %s x %s) is present but does not reads." % (dev_port, h, w))
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports, non_working_ports
camPort = list_ports()
# print(camPort)

vid = 0
mess = ""
model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
isMicrobitConnected = False
init_time = time.time()
counter = 5
cAI = 5
isFire = False
fires = 0
OS = platform.system()
node_name = "STM32" #for Linux OS
# dataTemp = 0
print("This OS is: ", OS)

if camPort[1].__len__() != 0:
    vid = cv2.VideoCapture(camPort[1][0])
else:
    print("no camera detected!!!")
    print("try wifi cam...")
    vid = cv2.VideoCapture('http://192.168.50.116:8080/video')


def counting(count, prev_time, period):
    now = time.time()
    #print("func called, now = ", now, " prev= ", prev_time)
    if now > prev_time + period:
        prev_time = now
        count = count - 1
        print("Looping: counter = ", count)
    return count, prev_time

while(True):
    counter, init_time = counting(counter, init_time, 1)
    if counter == cAI:
        cAI = cAI - 2
        if cAI <0: cAI = 5
        if vid != 0:
            ret, frame = vid.read()
            #cv2.imshow('frame', frame)
            res = model(frame)
            res.print()
            result = str(res)
            if result.__contains__("fire"):
                isFire = True
            else: isFire = False    
    if counter <= 0:
        counter = 30
        # if isMicrobitConnected:
        print("trying to read sensor and publish data...")
        try:
            print("Trying to read sersors from all serial ports")
            publishedJson = physicalSensors.buildJson()
        except Exception as ex:
            print('read sensor fail: ', ex)
            pass

        try:
            print("Trying to pushlish data")
            clientIOT = IOT.Client()
            clientIOT.publishFeed("nj1.jdata", publishedJson)
        except Exception as ex:
            print('pulish failed: ', ex)


        if isFire:
            fires = fires + 1
        else: fires = 0
        #false positive check: detect fire 2 time in a row
        if fires >= 2:
            print("FIRE!!!!!!!")

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    
  
## After the loop release the cap object
#vid.release()
## Destroy all the windows
#cv2.destroyAllWindows()
