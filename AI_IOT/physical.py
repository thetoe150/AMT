import time
import serial.tools.list_ports
import AQI
import json
import IOT

#TEMPERATURE = [3, 3, 0, 0, 0, 1, 133, 232]
#HUMIDITY = [3, 3, 0, 1, 0, 1, 212, 40]

#CO2 = [2, 3, 0, 4, 0, 1, 197, 248]
#PM2_5 = [4, 3, 0, 12, 0, 1, 68, 92]
#PM10 = [4, 3, 0, 13, 0, 1, 21, 156]

#NO2 = [0x0C, 0x03, 0x00, 0x02, 0x00, 0x01, 0x24, 0xD7]
#CO = [0x0E, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x35]
#SO2 = [0x0D, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x06]

#NITO = [1, 3, 0, 30, 0, 1, 228, 12]
#KALI = [1, 3, 0, 32, 0, 1, 133, 192]
#PHOTPHO = [1, 3, 0, 31, 0, 1, 181, 204]

#HUMIDITY_EPCB = [1, 3, 0, 0, 0, 1, 132, 10]
#TEMPERATURE_EPCB = [1, 3, 0, 1, 0, 1, 213, 202]
#EC_EPCB = [1, 3, 0, 2, 0, 1, 37, 202]
#PH_EPCB = [1, 3, 0, 3, 0, 1, 116, 10]

relay1_ON  = [0, 6, 0, 0, 0, 255, 200, 91]
relay1_OFF = [0, 6, 0, 0, 0, 0, 136, 27]

relay2_ON  = [15, 6, 0, 0, 0, 255, 200, 164]
relay2_OFF = [15, 6, 0, 0, 0, 0, 136, 228]

# list of sensors to loop through
sensors = {"temperature", "humidity", "co", "co2", "so2", "no2", "pm2_5", "pm10"}

sensors_write_bytes = {
    "temperature" : [3, 3, 0, 0, 0, 1, 133, 232],
    "humidity" : [3, 3, 0, 1, 0, 1, 212, 40],
    "co" : [0x0E, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x35],
    "co2": [2, 3, 0, 4, 0, 1, 197, 248],
    "so2": [0x0D, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x06],
    "no2": [0x0C, 0x03, 0x00, 0x02, 0x00, 0x01, 0x24, 0xD7],
    "pm2_5": [4, 3, 0, 12, 0, 1, 68, 92],
    "pm10":  [4, 3, 0, 13, 0, 1, 21, 156]
}

sensors_calibrate = {
    "temperature" : 0.1,
    "humidity" : 0.1,
    "co" : 1.0,
    "co2": 0.8,
    "so2": 1.0,
    "no2": 1.0,
    "pm2_5": 1.0,
    "pm10":  1.0
}

accuracy_truncate = {
    "temperature" : 0,
    "humidity" : 2,
    "co" : 1,
    "co2": 2,
    "so2": 0,
    "no2": 0,
    "pm2_5": 1,
    "pm10":  0
}
# The name of OS on window isn't Windows
#OS = platform.system
#if OS == "Windows":
    #deviceName = "USB Serial Port"
#else:
    #deviceName = "FT232R USB UART"

class Physical:
    def __init__(self):
        self.ports = []
        self.portsLength = 0

        self.sensorsData = {}

        self.sensorFaulty = False

        self.ports = self.getPortName()

        self.physicalClient = IOT.Client()

    def printAQI(self):

        for sensor in self.sensorsData:
            value = self.sensorsData[sensor][0]
            print(AQI.AQI.calculateAQI(sensor, value))

    def printData(self):
        for sensor in self.sensorsData:
            print(sensor, " value is: ", self.sensorsData[sensor])

    # find all port names string
    def getPortName(self):
        fullPortsName = serial.tools.list_ports.comports()
        self.portsLength = len(fullPortsName)
        commPort = []
        print('\n ---------Check for existing ports---------')
        if self.portsLength == 0:
            print('Detect no port')
        else: print('List of detected ports:')

        for i in range(0, self.portsLength):
            port = fullPortsName[i]
            strPort = str(port)
            print(strPort)

            # assum that the fisrt word is the port name
            splitPort = strPort.split(" ")
            commPort.append(splitPort[0])
        
        print()

        return commPort

    def setDevice1(self, ser, state):
        if state == True:
            ser.write(relay1_ON)
        else:
            ser.write(relay1_OFF)


    def setDevice2(self, ser, state):
        if state == True:
            ser.write(relay2_ON)
        else:
            ser.write(relay2_OFF)

    def serial_read_data(self, ser):
        bytesToRead = ser.inWaiting()
        if bytesToRead > 0:
            out = ser.read(bytesToRead)
            data_array = [b for b in out]
            if len(data_array) >= 7:
                array_size = len(data_array)
                value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
                return value
            else:
                return -1
        return -2

    def readSerial(self, serial, sensor_name):
        serial.write(sensors_write_bytes[sensor_name])
        time.sleep(1)
        return self.serial_read_data(serial) * sensors_calibrate[sensor_name]

    def readSensors(self):
        # check input serial ports every reading cycle
        #self.ports = self.getPortName()

        # loop through all detected ports
        for port_idx in range (self.portsLength):
            read_port = self.ports[port_idx]
            ser = serial.Serial(port = read_port, baudrate=9600) 

            print("--------Reading sensors of Port number ", read_port, "--------")

            # loop through all sensors of the detected port
            for sensor in sensors:
                print('Reading ', sensor, 'sensor', end=": ")
                data = self.readSerial(ser, sensor)

                if(data >= 0):
                    if sensor in self.sensorsData:
                        self.sensorsData[sensor].append(data)
                    else: # don't exist in dict
                        self.sensorsData[sensor] = [data]
                    print('read ', data)
                elif (data == -2):
                    print("have no sensor")
                else: 
                    print("fail to read sensor")

            #print("Controling relays of Port number ", self.ports[port_idx])
            #self.setDevice1(ser, True)
            #time.sleep(2)
            #self.setDevice1(ser, False)
            #time.sleep(2)
            #self.setDevice2(ser, True)
            #time.sleep(2)
            #self.setDevice2(ser, False)
            #time.sleep(2)
        self.printData()
        
    def analyzeData(self):
        for sensor in self.sensorsData:
            sensorCount = len(self.sensorsData[sensor])
            if  sensorCount > 1:
                sum = 0
                # max min for checking sensor failure
                max = 0
                min = 9999
                for value in self.sensorsData[sensor]:
                    sum += value 
                    if value > max:
                        max = value
                    if value < min:
                        min = value
                
                if max - min > 40:
                    self.sensorFaulty = True
                # will publish this average value to server
                average = sum / sensorCount
                if accuracy_truncate[sensor] == 0:
                    self.sensorsData[sensor][0] = int(average)
                else:
                    self.sensorsData[sensor][0] = round(average, accuracy_truncate[sensor])

                # only the average value remain
                del self.sensorsData[sensor][1:]
        
        self.printData()
        #self.printAQI()


    def buildJson(self):
        # check if any data have been read
        if not self.sensorsData:
            print('There is no sensor data to build Json')
            return ''
        
        jsonData = '{'
        for sensor in self.sensorsData:
            pubValue = self.sensorsData[sensor][0]

            if(pubValue == -1):
                jsonData += '"' + str(sensor) + '"' + ": " + '"sensor reading error"' + ', '
            elif (pubValue >= 0):
                aqi_val, category = AQI.AQI.calculateAQI(sensor, pubValue)
                if aqi_val == -1:
                    jsonData += '"' + str(sensor) + '"' + ": " + '{"value": ' + str(pubValue) + '}, '
                else:
                    jsonData += '"' + str(sensor) + '"' + ": " + '{"value": ' + str(pubValue) + \
                    ', "AQI": ' + str(aqi_val) + ', "quality": "' + category + '"}, '

        # TODO: sensor faulty 

        jsonData = jsonData[:-2] + '}'

        # check to see whether the string is correct in json format
        parsed = json.loads(jsonData)
        print(json.dumps(parsed, indent=4))

        return jsonData

    def publishData(self):
        json = self.buildJson()
        if json != '':
            self.physicalClient.publishFeed("nj1.jdata", json)

if __name__ == '__main__':
    physical = Physical()
    while True:
        physical.readSensors()
        physical.analyzeData()
        physical.publishData()
