import time
import platform
print("Sensors and Actuators")
import serial.tools.list_ports


OS = platform.system
deviceName = "FT232R USB UART"
def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if OS == "Windows":
            portStr = "USB Serial Device"
        else:
            portStr = deviceName
        if deviceName in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

portName = getPort()
print(portName)
if portName != "None":
    ser = serial.Serial(port=portName, baudrate=9600)

relay1_ON  = [0, 6, 0, 0, 0, 255, 200, 91]
relay1_OFF = [0, 6, 0, 0, 0, 0, 136, 27]

def setDevice1(state):
    if state == True:
        ser.write(relay1_ON)
    else:
        ser.write(relay1_OFF)

relay2_ON  = [15, 6, 0, 0, 0, 255, 200, 164]
relay2_OFF = [15, 6, 0, 0, 0, 0, 136, 228]

def setDevice2(state):
    if state == True:
        ser.write(relay2_ON)
    else:
        ser.write(relay2_OFF)




def serial_read_data(ser):
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        out = ser.read(bytesToRead)
        data_array = [b for b in out]
        print(data_array)
        if len(data_array) >= 7:
            array_size = len(data_array)
            value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
            return value/10
        else:
            return -1
    return 0

soil_temperature =[3, 3, 0, 0, 0, 1, 133, 232]
def readTemperature():
    serial_read_data(ser)
    ser.write(soil_temperature)
    time.sleep(1)
    return serial_read_data(ser)

soil_moisture = [3, 3, 0, 1, 0, 1, 212, 40]
def readMoisture():
    ser.write(soil_moisture)
    time.sleep(1)
    return serial_read_data(ser)

while True:
    # print("TEST MOTOR")
    # setDevice1(True)
    # time.sleep(2)
    # setDevice1(False)
    # time.sleep(2)
    #
    # setDevice2(True)
    # time.sleep(2)
    # setDevice2(False)
    # time.sleep(2)
    print("TEST SENSOR")
    print(readTemperature())
    print(readMoisture())
    time.sleep(2)
