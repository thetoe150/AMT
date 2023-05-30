import os
import threading
import multiprocessing as mp
import time
import psutil

def funx(n):
  return lambda a : a * n
def greetings(name):
  print("hello, ", name)
def my_function(arg1, arg2, kwarg1=None):
    # code here
    print(arg1+arg2)
    return kwarg1
def my_greetings():
    # code here
    print("henlo !")


def timeit(func, interval=0, *args, **kwargs):
    while True:
        start_time = time.time()
        result = func(*args, **kwargs)
        print("res:", result)
        end_time = time.time()
        print(f"Time taken to execute {func.__name__}: {end_time - start_time:.6f} seconds")
        time.sleep(interval)

def worker(num, func, intervals):
    print(f'Worker {num} started, Process ID: {os.getpid()}, Thread ID: {threading.get_ident()}')
    t0 = time.time()
    # simulate some work
    timeit(func,intervals)
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

print(mp.cpu_count())
#result = timeit(my_function, 5, 2, 3, kwarg1=9)
timeit(my_greetings,3)
timeit(greetings,5,"abcdf")