import threading

# create an atomic variable
shared_var = threading.AtomicInteger(0)

def writer():
    global shared_var
    # increment the shared variable
    shared_var.incrementAndGet()

def reader():
    global shared_var
    # read the shared variable
    value = shared_var.get()
    print("Value of shared variable: ", value)

# create two threads - one for writing and one for reading
t1 = threading.Thread(target=writer)
t2 = threading.Thread(target=reader)

# start the threads
t1.start()
t2.start()

# wait for both threads to complete
t1.join()
t2.join()