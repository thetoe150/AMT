import os
import threading
import time
import psutil

import threading
import time
import os

def worker(num):
    print(f'Worker {num} started, Process ID: {os.getpid()}, Thread ID: {threading.get_ident()}')
    t0 = time.time()
    # simulate some work
    time.sleep(1)
    t1 = time.time()
    if os.name == 'posix':
        # use sched_getaffinity for Linux/MacOS
        affinity = os.sched_getaffinity(0)
    else:
        # use cpu_affinity for Windows
        affinity = psutil.Process().cpu_affinity()

    if threading.get_ident() in affinity:
        print(f'Worker {num} completed, Process ID: {os.getpid()}, Thread ID: {threading.get_ident()}, '
              f'Physical Core: {affinity.index(threading.get_ident())//2}, '
              f'Logical Core: {affinity.index(threading.get_ident())%2}, '
              f'Time taken: {t1-t0:.6f} seconds')
    else:
        print(f'Worker {num} completed, Process ID: {os.getpid()}, Thread ID: {threading.get_ident()}, '
              f'not in CPU affinity list, Time taken: {t1-t0:.6f} seconds')


if __name__ == '__main__':
    start_time = time.time()
    # Create 5 worker threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)

    # Start the threads
    for t in threads:
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    end_time = time.time()

    print(f'All threads have completed, Total Time Taken: {end_time - start_time} seconds')
