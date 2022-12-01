import cv2
import torch
import time
import sys
import serial.tools.list_ports
from Adafruit_IO import MQTTClient
vid = cv2.VideoCapture(0)
model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
counter = 10
AIO_FEED_IDS =["led", "bbc-pump", "ai", "temp", "bbc-temp"]
AIO_USERNAME = "duy_ngotu"
AIO_KEY = "aio_YTrq60ESZzTgFii2z5P2vmZK8tDw"

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
    print("Nhan du lieu: " + payload)
    if isMicrobitConnected:
        ser.write((str(payload) + "#").encode())


client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_subscribe = subscribe
client.on_message = message
client.connect()
client.loop_background()

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial Device" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

isMicrobitConnected = False
if getPort() != "None":
    ser = serial.Serial(port=getPort(), baudrate=115200)
    isMicrobitConnected = True

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[1] == "temp":
            client.publish("bbc-temp", splitData[2])
    except:
        pass

mess = ""
def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]

while(True):
    ret, frame = vid.read()
    cv2.imshow('frame', frame)
    res = model(frame)
    print("Looping: c= ", counter)
    counter = counter - 1
    if counter <= 0:
        counter = 5
        if isMicrobitConnected:
            print("read microbit ")
            readSerial()
        else:
            print("microbit not connect, send random to temp feed ")
            client.publish("temp", -1)
    res.print()
    result = str(res)
    if result.__contains__("fire"):
        print("publish ai... ")
        client.publish("ai", "fire!")
    time.sleep(2)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
  
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()