import sqlite3
from datetime import datetime

import global_constant as gc

PHYSICAL_READ_TIME_INTERVAL = gc.PHYSICAL_READ_TIME_INTERVAL
NUMBER_OF_DATAPOINTS = gc.NUMBER_OF_DATAPOINTS
NUMBER_FOR_PREDICTION_DATA = gc.NUMBER_FOR_PREDICTION_DATA

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

class SensorDataStorage:
    def __init__(self):
        self.sensorType = []
        self.sensorDatabase = sqlite3.connect('air_monitoring.db', check_same_thread=False)
        self.sensorDataPoints = sqlite3.connect(':memory:', check_same_thread=False)
        self.initDatabase()

    def initDatabase(self):
        c = self.sensorDatabase.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS sensorDatabase (
            category TEXT,
            concentration FLOAT,
            date DATE)""")

        c = self.sensorDataPoints.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS sensorDataPoints (
            category TEXT,
            concentration FLOAT,
            date DATE
            )""")

        c = self.sensorDatabase.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS sensorDataCalib (
            category TEXT,
            calib TEXT,
            date DATE
            )""")
        
        self.sensorDatabase.commit()
        self.sensorDataPoints.commit()

    def printDataPoint(self):
        c = self.sensorDataPoints.cursor()
        c.execute("SELECT * FROM sensorDataPoints")
        print("Data Point: ", c.fetchall())

    def printDatabase(self):
        c = self.sensorDatabase.cursor()
        c.execute("SELECT * FROM sensorDatabase")
        print("Database: ", c.fetchall())

    def printDataCalib(self):
        c = self.sensorDatabase.cursor()
        c.execute("SELECT * FROM sensorDataCalib")
        print("Data Point: ", c.fetchall())

    def updateDataCalib(self, sensor, value):
        now = datetime.now()
        date = now.strftime('%Y-%m-%d %H:%M:%S')

        c = self.sensorDatabase.cursor()

        c.execute("DELETE FROM sensorDataCalib\
                WHERE category = :category", 
                {'category': sensor})

        c.execute("INSERT INTO sensorDataCalib \
                VALUES (:category, :calib, :date)", 
            {'category': sensor, 'calib': value, 'date': date})

        self.sensorDatabase.commit()

    def getDataCalib(self, sensor):
        c = self.sensorDatabase.cursor()
        c.execute("SELECT * FROM sensorDataCalib\
                WHERE category = :category",
                  {'category': sensor})

        res = c.fetchall() 
        if not res:
            return -1

        return res[0][1]

    def addDataPoints(self, sensorsData):
        c = self.sensorDataPoints.cursor()
        now = datetime.now()
        date = now.strftime('%Y-%m-%d %H:%M:%S')
        try:
            # sensorData is a dict of various type of sensor
            for sensor in sensorsData:

                value = sensorsData[sensor][0]
                if value == -1:
                    # the case when data is invalid
                    continue

                if sensor not in self.sensorType:
                    self.sensorType.append(sensor)

                print('inside addd Data POint', value)

                c.execute("INSERT INTO sensorDataPoints \
                        VALUES (:category, :concentration, :date)", 
                          {'category': sensor, 'concentration': float(value), 'date': date})

        except Exception as e:
            print(e)
            self.sensorDataPoints.rollback()

        self.printDataPoint()
        self.sensorDataPoints.commit()

    def dumpDataPoints(self):

        now = datetime.now()
        date = now.strftime('%Y-%m-%d %H:%M:%S')
        print(date)

        res = {}
        # retrive data for each type of sensor from the memory database
        for sensor in self.sensorType:
            c = self.sensorDataPoints.cursor()
            c.execute("SELECT * FROM sensorDataPoints \
             WHERE category = :category\
             ORDER BY date DESC LIMIT :dataPointNum",\
             {'category' : sensor, 'dataPointNum' : NUMBER_OF_DATAPOINTS})
            dataPoint = c.fetchall()
            
            if dataPoint:
                store_data = 0
                data_length = len(dataPoint)
                if data_length == 0:
                    continue
                # loop through data in form of python tuple of each sensors
                for data in dataPoint:
                    print(data[1])
                    store_data += data[1]  # concentration is at the 2th posion of the tuple

                print("length of data point = ", data_length)
                print("data Point of {}: {}".format(sensor, dataPoint))
                # average value
                store_data /= data_length
                # return res containing hourly average for calculating AQI
                
                res[sensor] = round(store_data, accuracy_truncate[sensor])


                # insert this hourly average into database
                c = self.sensorDatabase.cursor()
                c.execute("INSERT INTO sensorDatabase VALUES (:category, :concentration, :date)", 
                        {'category': sensor, 'concentration': store_data, 'date': date})

        self.sensorDatabase.commit()

        # only trim a part of the database not delete every records
        # because validate() method need older record to analyze data
        self.trimDataPoints()

        return res

    def trimDataPoints(self):
        c = self.sensorDataPoints.cursor()
        c.execute("SELECT COUNT(*) FROM sensorDataPoints")
        # fetchall seem to always return an array of tuple
        recordNum = c.fetchall()[0][0]
        print('in trimDatabase(): numbers of datapoints records: ', recordNum)

        # this hard code number 8 thing is bad
        remainRec = NUMBER_FOR_PREDICTION_DATA * 8
        if remainRec > recordNum:
            return 0
        
        deletedRec = recordNum - remainRec
        c.execute("DELETE FROM sensorDataPoints\
                WHERE date IN  \
                    (SELECT date \
                    FROM sensorDataPoints \
                    WHERE 1 = 1 \
                    ORDER BY date ASC LIMIT :deletedRec)",\
                {'deletedRec' : deletedRec})
        self.sensorDatabase.commit()

        return deletedRec

    
    def getDataPoints(self, sensor_type):
        c = self.sensorDataPoints.cursor()
        c.execute("SELECT * FROM sensorDataPoints \
         WHERE category = :category",\
         {'category' : sensor_type})
        res = []
        data = c.fetchall()
        for item in data:
            res.append(item[1])

        return res

    def getDataBase(self, sensor_type, data_num):
        c = self.sensorDatabase.cursor()
        c.execute("SELECT * FROM sensorDatabase \
         WHERE category = :category\
         ORDER BY date DESC LIMIT :dataPointNum",\
         {'category' : sensor_type, 'dataPointNum' : data_num})
        res = []
        data = c.fetchall()
        for item in data:
            res.append(item[1])

        return res

    def selectByDate(self):
        c = self.sensorDatabase.cursor()
        c.execute("SELECT * FROM sensorDatabase \
         WHERE category = :category\
         ORDER BY date DESC LIMIT :dataPointNum",\
         {'category' : 'pm2_5', 'dataPointNum' : NUMBER_OF_DATAPOINTS})
        dataPoint = c.fetchall()
        c.execute("SELECT COUNT(*) FROM sensorDatabase")
        print('number of record in sensors database',c.fetchall()[0][0])
        return dataPoint
        
    def tableInfo(self):
        c = self.sensorDataPoints.cursor()
        c.execute('PRAGMA table_info(sensorDataPoints)')
        print(c.fetchall())

    def resetDataPoints(self):
        c = self.sensorDataPoints.cursor()
        c.execute("DELETE  FROM sensorDataPoints")
        self.sensorDataPoints.commit()

    def deleteDataPoints(self):
        c = self.sensorDataPoints.cursor()
        c.execute("DROP TABLE sensorDataPoints")
        self.sensorDataPoints.commit()

    def resetDatabase(self):
        c = self.sensorDatabase.cursor()
        c.execute("DELETE  FROM sensorDatabase")
        self.sensorDatabase.commit()

    def resetDataCalib(self):
        c = self.sensorDatabase.cursor()
        c.execute("DELETE  FROM sensorDataCalib")
        self.sensorDatabase.commit()

if __name__ == '__main__':
    data1 = {
        'CO2' : [105],
        'NO2' : [45],
        'O3' : [12],
        'Temperature' : [25],
    }
    data2 = {
        'CO2' : [50],
        'NO2' : [15],
        'O3' : [12],
        'Temperature' : [40],
    }
    data3 = {
        'CO2' : [20],
        'NO2' : [15],
        'O3' : [12],
    }

    dataStorage = SensorDataStorage()
    #dataStorage.printDatabase()
    # dataStorage.resetDatabase()
    #dataStorage = SensorDataStorage()
    # dataStorage.tableInfo()
    dataStorage.resetDatabase()

    # dataStorage.updateDataCalib("pm2_5", 34)
    # dataStorage.updateDataCalib("pm2_5", 34)
    # dataStorage.updateDataCalib("co", 34)
    # dataStorage.updateDataCalib("temperature", 34)
    #dataStorage.printDataCalib()
    print(dataStorage.getDataCalib("pm2_5"))
    print(dataStorage.getDataCalib("co"))
    print(dataStorage.getDataCalib("hehe"))

    

    #print(dataStorage.selectByDate())
    #print(PHYSICAL_READ_TIME_INTERVAL)
