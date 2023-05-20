import platform
import threading
import multiprocessing
from time import time, sleep
from datetime import datetime

import physical
import ai

OS = platform.system()
# dataTemp = 0
print("This OS is: ", OS)

PHYSICAL_READ_TIME_INTERVAL = 10
NUMBER_OF_DATAPOINTS = 2
PHYSICAL_PUBLISH_TIME_INTERVAL = PHYSICAL_READ_TIME_INTERVAL * NUMBER_OF_DATAPOINTS

SYSTEM_COMPONENT_COUNTER = {
    # CPU bounded - often takes around 2s
    # recieve number should be > 3
    'AI_Camera' : 4,
    # IO bounded - takes 1s for each of 16 total sensors
    # recieve number should be > 20
    'Physical' : PHYSICAL_READ_TIME_INTERVAL, 
    'PublishingPhysical' : PHYSICAL_PUBLISH_TIME_INTERVAL
}

class systemAMT:
    def __init__(self):
        print('Initialing System with Thread {} executing at: {}'.format(threading.get_ident(), datetime.now()) ,end=' ')
        self.physicalSensors = physical.Physical()
        self.aiCamera = ai.AICam()
        self.thread_list = []

    def componentThread(self, name, interval):

        while True:
            start_time = time()
            now = datetime.now()
            date = now.strftime('%Y-%m-%d %H:%M:%S')
            print('Thread {} executing at: {}'.format(threading.get_ident(), date) ,end=' ')
            print(date)

            if name == 'Physical':
                try:
                    print("******************* Trying to read sersors from all serial ports *******************")
                    self.physicalSensors.readSensors()
                    self.physicalSensors.analyzeData()
                    self.physicalSensors.storeInstanceData()
                    print('Time take to read sensor: ', str(time() - start_time))
                except Exception as ex:
                    print('read sensor fail: ', ex)

            if name == 'PublishingPhysical':
                try:
                    print("******************* Trying to publish sensors data to server *******************")
                    self.physicalSensors.getAverageData()
                    self.physicalSensors.publishData()
                    print('Time take to read sensor: ', str(time() - start_time))
                except Exception as ex:
                    print('read sensor fail: ', ex)

            if name == 'AI_Camera':
                try:
                    print("******************* Trying to detect fire from all cam ports *******************")
                    self.aiCamera.readCams()
                    self.aiCamera.readInferedCam()
                    self.get_alert_level_wo_sensor()
                    self.aiCamera.publishData()
                    print('Time take to read camera: ', str(time() - start_time))
                except Exception as ex:
                    print('detect fire fail:', ex)


            remain_time = interval - (time() - start_time)
            if remain_time > 0:
                sleep(remain_time)

    def runThreading(self):        
        for name, interval in SYSTEM_COMPONENT_COUNTER.items():
            #process = multiprocessing.Process(target=call_hello, args=(name, interval))
            process = threading.Thread(target=self.componentThread, args=(name, interval))
            self.thread_list.append(process)
            process.start()

        for process in self.thread_list:
            process.join()

if __name__ == "__main__":

    system = systemAMT()
    system.runThreading()
