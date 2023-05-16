from dotenv import load_dotenv
from Adafruit_IO import MQTTClient
import os
import sys

AIO_FEED_IDS = ['nj1.jdata', 'nj1.isfire', 'nj1.mpollutant', 'nj1.maqi', 'nj1.temp', 'nj1.humid']
load_dotenv()
AIO_USERNAME = os.environ.get('ADAFRUIT_IO_USERNAME')
AIO_KEY = os.environ.get('ADAFRUIT_IO_KEY')

def connected(client):
    print("Connect successfully")
    for feed in AIO_FEED_IDS:
        client.subscribe(feed)

def subscribe(client, userdata, mid, granted_qos):
    print("Subcribe successfully")

def disconnected(client):
    print("Disconnected")
    sys.exit (1)

def message(client, feed_id, payload):
    print("hello")
    #if isMicrobitConnected:
        #ser.write((str(payload) + "#").encode())
        #if feed_id == "led":
            #if payload == "1":
                ##print("command relay on\n")
                ##ser.write(str.encode('LED_ONN'))
                #setDevice1(True)
            #if payload == "0":
                ##print("command relay off\n")
                ##ser.write(str.encode('LED_OFF'))
                #setDevice1(False)


class Client:
    def __init__(self):
        self.client = MQTTClient(AIO_USERNAME, AIO_KEY)
        self.client.on_connect = connected
        self.client.on_disconnect = disconnected
        self.client.on_subscribe = subscribe
        self.client.on_message = message
        self.client.connect()
        self.client.loop_background()


    def publishFeed(self, feedName, data):
        print('Publishing json: ')
        self.client.publish(feedName, data)
        print(data)
    
    def receiveFeed(self, feedName):
        self.client.receive(feedName).value
