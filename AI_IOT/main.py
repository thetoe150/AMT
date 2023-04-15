import platform
import threading
import multiprocessing
from time import time, gmtime, sleep, asctime

import physical
import ai
import IOT

OS = platform.system()
node_name = "STM32" #for Linux OS
# dataTemp = 0
print("This OS is: ", OS)

SYSTEM_COMPONENT_COUNTER = {
    'AI_Camera' : 3,
    'Physical' : 60,
    'IOT_Client': 6
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
        self.clientIOT = IOT.Client()
        self.thread_list = []

        self.physicalJson = ''
        self.fireJson = ''

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
                    self.physicalJson = self.physicalSensors.buildJson()
                except Exception as ex:
                    print('read sensor fail: ', ex)

            if name == 'AI_Camera':
                try:
                    print("******************* Trying to detect fire from all cam ports *******************")
                    self.aiCamera.readCams()
                    self.fireJson = self.aiCamera.buildJson()
                except Exception as ex:
                    print('detect fire fail:', ex)


            if name == 'IOT_Client':
                try:
                    print("******************* Trying to pushlish data from both sensors and cams *******************")
                    if self.physicalJson != '':
                        self.clientIOT.publishFeed("nj1.jdata", self.physicalJson)

                    if self.fireJson != '':
                        self.clientIOT.publishFeed("nj1.isfire", self.fireJson)
                        
                except Exception as ex:
                    print('pulish data failed: ', ex)

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
