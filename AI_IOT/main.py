import platform
import threading
import multiprocessing
from time import time, sleep
from datetime import datetime
import sys

import global_constant as gc
import physical
import ai
import log

OS = platform.system()
# dataTemp = 0
print("This OS is: ", OS)

def GetDebugOption():
    n = len(sys.argv)
    for str in range(1, n):
        if(sys.argv[str] == '-d'):
            return True
    
    return False

CAM_READ_TIME_INTERVAL = gc.CAM_READ_TIME_INTERVAL
PHYSICAL_READ_TIME_INTERVAL = gc.PHYSICAL_READ_TIME_INTERVAL
NUMBER_OF_DATAPOINTS = gc.NUMBER_OF_DATAPOINTS
PHYSICAL_PUBLISH_TIME_INTERVAL = PHYSICAL_READ_TIME_INTERVAL * NUMBER_OF_DATAPOINTS + 1

SYSTEM_COMPONENT_COUNTER = {
    # CPU bounded - often takes around 2s
    # recieve number should be > 3
    'AI_Camera' : CAM_READ_TIME_INTERVAL,
    # IO bounded - takes 1s for each of 16 total sensors
    # recieve number should be > 20
    'Physical' : PHYSICAL_READ_TIME_INTERVAL, 
    'PublishingPhysical' : PHYSICAL_PUBLISH_TIME_INTERVAL
}

def GetAlertLevel(isFireCam, isFireSensor):
    # cam have 3 stage
    # None
    # Low
    # High

    # sensors have 3 stage
    # 0: don't have sensors or we don't consider sensors data
    # 1: Usual data
    # 2: Unpredicted data

    if isFireCam == 'None':
        return 'None'
    if isFireSensor == 0: # the case we don't consider sensor data
        return isFireCam
    else:
        if isFireCam == 'Low' and isFireSensor == 1:
            return 'Low'
        if isFireCam == 'Low' and isFireSensor == 2:
            return 'Low'
        if isFireCam == 'High' and isFireSensor == 1:
            return 'Medium'
        if isFireCam == 'High' and isFireSensor == 2:
            return 'High'

    # return value has 4 possible stage
    # None
    # Low
    # Medium
    # High


class systemAMT:
    def __init__(self, isDebug):
        print('Initialing System with Thread {} executing at: {}'.format(threading.get_ident(), datetime.now()) ,end=' ')
        self.physicalSensors = physical.Physical(isDebug)
        self.aiCamera = ai.AICam(isDebug)
        self.thread_list = []

        self.isFireCam = "None"
        self.isFireSensor = 0

        self.log = log.setupLogger('thread_log', 'log/thread.log')

    def componentThread(self, name, interval):

        while True:
            start_time = time()
            self.log.info('Thread {} is executed'.format(threading.get_ident()))

            if name == 'Physical':
                try:
                    print("******************* Trying to read sersors from all serial ports *******************")
                    self.physicalSensors.readSensors()
                    self.physicalSensors.validateData()
                    self.isFireSensor = self.physicalSensors.setIsFireSensor()
                    print('Sensor detect fire: {}'.format(self.isFireSensor))
                    self.physicalSensors.storeInstanceData()

                    self.log.info('Time to read sensor: {} from thread {}'.format(str(time() - start_time), threading.get_ident()))
                except Exception as ex:
                    self.log.error('Failed to read sensor: {}'.format(ex))

            elif name == 'PublishingPhysical':
                try:
                    print("******************* Trying to publish sensors data to server *******************")
                    self.physicalSensors.getAverageData()
                    self.physicalSensors.publishData()
                    self.log.info('Time to publish AQI: {} from thread {}'.format(str(time() - start_time), threading.get_ident()))
                except Exception as ex:
                    self.log.error('Failed to publish sensor data: {}'.format(ex))

            elif name == 'AI_Camera':
                try:
                    print("******************* Trying to detect fire from all cam ports *******************")
                    self.aiCamera.readCams()
                    self.aiCamera.readInferedCam()
                    self.isFireCam = self.aiCamera.setIsFireCam()
                    print('Camera detect fire: {}'.format(self.isFireCam))
                    res = GetAlertLevel(self.isFireCam, self.isFireSensor)
                    print('Level of fire warning: {}'.format(res))
                    self.aiCamera.publishData(res)
                    self.log.info('Time to read cam and detect fire: {} from thread {}'.format(str(time() - start_time), threading.get_ident()))
                except Exception as ex:
                    self.log.error('Failed to read cam and detect fire: {}'.format(ex))


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
    IsDebug = GetDebugOption()

    system = systemAMT(IsDebug)
    system.runThreading()
