import platform
import threading
import multiprocessing
from time import time, gmtime, sleep, asctime

import database
import physical
import ai

OS = platform.system()
node_name = "STM32" #for Linux OS
# dataTemp = 0
print("This OS is: ", OS)

SYSTEM_COMPONENT_COUNTER = {
    # CPU bounded - often takes around 2s
    # recieve number should be > 3
    'AI_Camera' : 10,  
    # IO bounded - takes 1s for each of 16 total sensors
    # recieve number should be > 20
    'Physical' : 10    
}

def counting(count, prev_time, period):
    now = time()
    #print("func called, now = ", now, " prev= ", prev_time)
    if now > prev_time + period:
        prev_time = now
        count = count - 1
        print("Looping: counter = ", count)
    return count, prev_time

class systemAMT:
    def __init__(self):
        print("******************* Trying to read sersors from all serial ports *******************")
        self.physicalSensors = physical.Physical()
        self.aiCamera = ai.AICam()
        self.thread_list = []

    def componentThread(self, name, interval):

        while True:
            start_time = time()
            print('At', end=' ')
            print(asctime(gmtime(start_time)))

            if name == 'Physical':
                try:
                    print("******************* Trying to read sersors from all serial ports *******************")
                    self.physicalSensors.readSensors()
                    self.physicalSensors.analyzeData()
                    self.physicalSensors.publishData()
                    print('Time take to read sensor: ', str(time() - start_time))
                except Exception as ex:
                    print('read sensor fail: ', ex)

            if name == 'AI_Camera':
                try:
                    print("******************* Trying to detect fire from all cam ports *******************")
                    self.aiCamera.readCams()
                    self.aiCamera.processImages()
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



#CPU_CONST = 10000
#IO_CONST = 10

#def CPU_bound_func(name):
    #time.sleep(IO_CONST)

#def CPU_bound_func(name, interval):
    #i = 0
    #while i < CPU_CONST:
        #i = i + 1
