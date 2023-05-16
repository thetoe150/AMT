import multiprocessing as mp
import time
from datetime import datetime
from datetime import datetime


def show_time():
    timestamp = time.time()
    formatted_time = datetime.fromtimestamp(timestamp).strftime('%d/%m/%y %H:%M:%S.%f')[:-3]
    print(formatted_time)

def function1(shared_value1, shared_value2, interval):
    process = mp.current_process()
    
    while True:
        start_time = time.time()
        
        # Modify shared_value1
        shared_value1.value += 1
        
        end_time = time.time()
        show_time()
        print(f"Process {process.name} (ID: {process.pid}) - Value1: {shared_value1.value}, Value2: {shared_value2.value}, Time: {end_time - start_time} seconds\n")
        
        time.sleep(interval)

def function2(shared_value1, shared_value2, interval):
    process = mp.current_process()
    
    while True:
        start_time = time.time()
        
        # Access shared_value1 and shared_value2
        #print(f"Value1 from function1: {shared_value1.value}")
        #print(f"Value2 from function3: {shared_value2.value}")
        
        end_time = time.time()
        show_time()
        print(f"Process {process.name} (ID: {process.pid}) - Value1: {shared_value1.value}, Value2: {shared_value2.value}, Time: {end_time - start_time} seconds\n")
 
        time.sleep(interval)

def function3(shared_value1, shared_value2, interval):
    process = mp.current_process()
    
    while True:
        start_time = time.time()
        
        # Modify shared_value2
        shared_value2.value *= 2
        shared_value1.value *= 2
        end_time = time.time()
        show_time()
        print(f"Process {process.name} (ID: {process.pid}) - Value1: {shared_value1.value}, Value2: {shared_value2.value}, Time: {end_time - start_time} seconds\n")
        
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
#    process2 = mp.Process(target=function2, args=(shared_value1, shared_value2, 3))
    process3 = mp.Process(target=function3, args=(shared_value1, shared_value2, 3))
#   process4 = mp.Process(target=function4, args=(shared_value1, shared_value2, 5))
    
    process1.start()
#   process2.start()
    process3.start()
#   process4.start()
    
    time.sleep(15)  # Run the processes for 10 seconds
    
    process1.terminate()
#    process2.terminate()
    process3.terminate()
#   process4.terminate()
    
    process1.join()
#    process2.join()
    process3.join()
#    process4.join()
