import cv2
import torch
import time
import sys
import serial.tools.list_ports
from Adafruit_IO import MQTTClient
import os
import platform
from dotenv import load_dotenv
import physical



AIO_FEED_IDS =["nanojetson.co", "nanojetson.co2", "nanojetson.no2", "nanojetson.so2", "nanojetson.humidity", "nanojetson.temperature"]
load_dotenv()
AIO_USERNAME = os.environ.get('ADAFRUIT_IO_USERNAME')
AIO_KEY = os.environ.get('ADAFRUIT_IO_KEY')


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

if camPort[1].__len__() == 0:
    vid = cv2.VideoCapture(camPort[1][1])
else:
    print("no camera detected!!!")
    print("try wifi cam...")
    vid = cv2.VideoCapture('http://192.168.50.116:8080/video')

def  connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_IDS:
        client.subscribe(feed)

def  subscribe(client , userdata , mid , granted_qos):
    print("Subcribe thanh cong...")

def  disconnected(client):
    print("Ngat ket noi...")
    sys.exit (1)

def  message(client , feed_id , payload):
    print("Nhan du lieu: " + payload, " feeid:" + feed_id)
    if isMicrobitConnected:
        ser.write((str(payload) + "#").encode())
        if feed_id == "led":
            if payload == "1":
                #print("command relay on\n")
                #ser.write(str.encode('LED_ONN'))
                setDevice1(True)
            if payload == "0":
                #print("command relay off\n")
                #ser.write(str.encode('LED_OFF'))
                setDevice1(False)


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_subscribe = subscribe
client.on_message = message
client.connect()
client.loop_background()

# def getPort():
#     ports = serial.tools.list_ports.comports()
#     print(ports)
#     N = len(ports)
#     commPort = "None"
#     for i in range(0, N):
#         port = ports[i]
#         strPort = str(port)
#         print(strPort)
#         if OS == 'Windows':
#             portStr = "USB Serial Device"
#         else:
#             portStr = node_name
#         if portStr in strPort:
#             splitPort = strPort.split(" ")
#             commPort = (splitPort[0])
#     return commPort

# if getPort() != "None":
#     ser = serial.Serial(port=getPort(), baudrate=115200)
#     isMicrobitConnected = True

# def processData(data):
#     data = data.replace("!", "")
#     data = data.replace("#", "")
#     splitData = data.split(":")
#     print(splitData)
#     # try:
#     if splitData[0] == "temp":
#         return splitData[1]
#             # client.publish("temp", splitData[1])
#             # print('publishing....')
#     # except:
#     #     print('pulish failed')
    #     pass

# def readSerial():
#     data = -1
#     bytesToRead = ser.inWaiting()
#     if (bytesToRead > 0):
#         global mess
#         mess = mess + ser.read(bytesToRead).decode("UTF-8")
#         while ("#" in mess) and ("!" in mess):
#             start = mess.find("!")
#             end = mess.find("#")
#             data = processData(mess[start:end + 1])
#             if (end == len(mess)):
#                 mess = ""
#             else:
#                 mess = mess[end+1:]
#     print(data)
#     return data
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
        print("publish data...")
        try:
            temp = physical.readTemperature()
            mois = physical.readHumidity()
            so2 = physical.readSO2()
            no2 = physical.readNO2()
            co = physical.readCO()
            co2 = physical.readCO2()
            # print("Data to pulish: ", dataToPush)
            client.publish("nanojetson.temperature", temp)
            print('publishing temperature....')
            client.publish("nanojetson.humidity", mois)
            print('publishing humidity...')
            client.publish("nanojetson.so2", so2)
            print('publishing so2....')
            client.publish("nanojetson.no2", no2)
            print('publishing no2...')
            client.publish("nanojetson.co", co)
            print('publishing co....')
            client.publish("nanojetson.co2", co2)
            print('publishing co2...')

        except:
            print('pulish failed')
            pass
        # else:
        #     print("microbit not connect, send -1 to temp feed ")
        #     client.publish("temp", -1)
        if isFire:
            fires = fires + 1
        else: fires = 0
        #false positive check: detect fire 2 time in a row
        if fires >= 2:
            print("publish ai... ")
            client.publish("ai", "there is fire!")
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    
  
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
