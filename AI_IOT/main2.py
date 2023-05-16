import platform
import threading
import multiprocessing
from time import time, sleep
from datetime import datetime
import physical
import ai

OS = platform.system()
print("This OS is: ", OS)

PHYSICAL_READ_TIME_INTERVAL = 10
NUMBER_OF_DATAPOINTS = 2
PHYSICAL_PUBLISH_TIME_INTERVAL = PHYSICAL_READ_TIME_INTERVAL * NUMBER_OF_DATAPOINTS

SYSTEM_COMPONENT_COUNTER = {
    # CPU bounded - often takes around 2s
    # recieve number should be > 3
    'AI_Camera' : 60,
    # IO bounded - takes 1s for each of 16 total sensors
    # recieve number should be > 20
    'Physical' : PHYSICAL_READ_TIME_INTERVAL, 
    'PublishingPhysical' : PHYSICAL_PUBLISH_TIME_INTERVAL
}


def show_time():
    timestamp = time.time()
    formatted_time = datetime.fromtimestamp(timestamp).strftime('%d/%m/%y %H:%M:%S.%f')[:-3]
    print(formatted_time)

#sensor-related process
def function1(shared_value1, shared_value2, interval):
    process = mp.current_process()
    
    while True:
        start_time = time.time()
        
        # Call the worker functions
        try:
            print("******************* Trying to read sersors from all serial ports *******************")
            self.physicalSensors.readSensors()
            self.physicalSensors.analyzeData()
            self.physicalSensors.storeInstanceData()
        except Exception as ex:
            print('read sensor fail: ', ex)
        ###########################

        end_time = time.time()
        show_time()
        print(f"Process {process.name} (ID: {process.pid}), Time: {end_time - start_time} seconds\n")
        
        time.sleep(interval)

#AIcamera process
def function2(shared_value1, shared_value2, interval):
    process = mp.current_process()
    
    while True:
        start_time = time.time()


        # Call the worker functions
        try:
            print("******************* Trying to detect fire from all cam ports *******************")
            self.aiCamera.readCams()
            self.aiCamera.processImages()
            self.aiCamera.publishData()
        except Exception as ex:
            print('detect fire fail:', ex)
        ###########################



        end_time = time.time()
        show_time()
        print(f"Process {process.name} (ID: {process.pid}), Time: {end_time - start_time} seconds\n")
 
        time.sleep(interval)


#Publishing sensor data
def function3(shared_value1, shared_value2, interval):
    process = mp.current_process()
    
    while True:
        start_time = time.time()
        

        # Call the worker functions
        try:
            print("******************* Trying to publish sensors data to server *******************")
            self.physicalSensors.getAverageData()
            self.physicalSensors.publishData()
            print('Time take to read sensor: ', str(time() - start_time))
        except Exception as ex:
            print('read sensor fail: ', ex)
        ###########################


        end_time = time.time()
        show_time()
        print(f"Process {process.name} (ID: {process.pid}), Time: {end_time - start_time} seconds\n")
        
        time.sleep(interval)

def function4(shared_value1, shared_value2, interval):
    process = mp.current_process()
    
    while True:
        start_time = time.time()
        
        # Access shared_value1 and shared_value2
        print(f"Value1 from function3: {shared_value1.value}")
        print(f"Value2 from function3: {shared_value2.value}")
        
        end_time = time.time()
        show_time()
        print(f"Process {process.name} (ID: {process.pid}) completed in {end_time - start_time} seconds.")
        
        time.sleep(interval)

if __name__ == '__main__':
    shared_value1 = mp.Value('i', 0)
    shared_value2 = mp.Value('i', 10)
    interval = 2
    
    process1 = mp.Process(target=function1, args=(shared_value1, shared_value2, 2))
    process2 = mp.Process(target=function2, args=(shared_value1, shared_value2, 3))
    process3 = mp.Process(target=function3, args=(shared_value1, shared_value2, 3))
#   process4 = mp.Process(target=function4, args=(shared_value1, shared_value2, 5))
    
    process1.start()
    process2.start()
    process3.start()
#   process4.start()
    
#    time.sleep(10)  # Run the processes for 10 seconds
    
#    process1.terminate()
#    process2.terminate()
#    process3.terminate()
#   process4.terminate()
    
    process1.join()
    process2.join()
    process3.join()
#    process4.join()
