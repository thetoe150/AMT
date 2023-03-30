import time
import platform
import serial.tools.list_ports

print("Sensors and Actuators")

TEMPERATURE = [3, 3, 0, 0, 0, 1, 133, 232]
HUMIDITY = [3, 3, 0, 1, 0, 1, 212, 40]

CO2 = [2, 3, 0, 4, 0, 1, 197, 248]
PM2_5 = [4, 3, 0, 12, 0, 1, 68, 92]
PM10 = [4, 3, 0, 13, 0, 1, 21, 156]

NO2 = [0x0C, 0x03, 0x00, 0x02, 0x00, 0x01, 0x24, 0xD7]
CO = [0x0E, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x35]
SO2 = [0x0D, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x06]

NITO = [1, 3, 0, 30, 0, 1, 228, 12]
KALI = [1, 3, 0, 32, 0, 1, 133, 192]
PHOTPHO = [1, 3, 0, 31, 0, 1, 181, 204]

HUMIDITY_EPCB = [1, 3, 0, 0, 0, 1, 132, 10]
TEMPERATURE_EPCB = [1, 3, 0, 1, 0, 1, 213, 202]
EC_EPCB = [1, 3, 0, 2, 0, 1, 37, 202]
PH_EPCB = [1, 3, 0, 3, 0, 1, 116, 10]

# The name of OS on window isn't Windows
#OS = platform.system
#if OS == "Windows":
    #deviceName = "USB Serial Port"
#else:
    #deviceName = "FT232R USB UART"

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        print(strPort)

        # assum that the fisrt word is the port name
        splitPort = strPort.split(" ")
        commPort = (splitPort[0])
    return commPort

portName = getPort()
print(portName)
if portName != "None":
    ser = serial.Serial(port=portName, baudrate=9600)
else:
    print("Found no Port")

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

def readTemperature():
    print('Temperature:')
    ser.write(TEMPERATURE)
    time.sleep(1)
    return serial_read_data(ser)

def readHumidity():
    print('Humidity:')
    ser.write(HUMIDITY)
    time.sleep(1)
    return serial_read_data(ser)

def readCO():
    print('CO:')
    ser.write(CO)
    time.sleep(1)
    return serial_read_data(ser)

def readSO2():
    print('SO2:')
    ser.write(SO2)
    time.sleep(1)
    return serial_read_data(ser)

def readNO2():
    print('NO2:')
    ser.write(NO2)
    time.sleep(1)
    return serial_read_data(ser)

def readPM2_5():
    print('PM2_5:')
    ser.write(PM2_5)
    time.sleep(1)
    return serial_read_data(ser)

def readPM10():
    print('PM10:')
    ser.write(PM10)
    time.sleep(1)
    return serial_read_data(ser)

#while True:
    #print("TEST MOTOR")
    #setDevice1(True)
    #time.sleep(2)
    #setDevice1(False)
    #time.sleep(2)
    #setDevice2(True)
    #time.sleep(2)
    #setDevice2(False)
    #time.sleep(2)
    #print("TEST SENSOR")
    #print(readTemperature())
    #print(readHumidity())
    #print(readNO2())
    #print(readCO())
    #print(readSO2())
    #print(readPM2_5())
    #print(readPM10())
    #time.sleep(2)
