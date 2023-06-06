import sqlite3
from datetime import datetime

import global_constant as gc

PHYSICAL_READ_TIME_INTERVAL = gc.PHYSICAL_READ_TIME_INTERVAL
NUMBER_OF_DATAPOINTS = gc.NUMBER_OF_DATAPOINTS
NUMBER_OF_PREDICTION_DATA = gc.NUMBER_OF_PREDICTION_DATA

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
            date DATE
            )""")

        c = self.sensorDataPoints.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS sensorDataPoints (
            category TEXT,
            concentration FLOAT,
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

    def addDataPoints(self, sensorsData):
        c = self.sensorDataPoints.cursor()
        now = datetime.now()
        date = now.strftime('%Y-%m-%d %H:%M:%S')
        try:
            # sensorData is a dict of various type of sensor
            for sensor in sensorsData:
                if sensor not in self.sensorType:
                    self.sensorType.append(sensor)

                c.execute("INSERT INTO sensorDataPoints \
                        VALUES (:category, :concentration, :date)", 
                        {'category': sensor, 'concentration': sensorsData[sensor][0],\
                                'date': date})

        except Exception as e:
            print(e)
            self.sensorDataPoints.rollback()

        self.sensorDataPoints.commit()
        self.printDataPoint()

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
                # loop through data in form of python tuple of each sensors
                for data in dataPoint:
                    store_data += data[1]  # concentration is at the 2th posion of the tuple

                print("length of data point = ", len(dataPoint))
                print("data Point of {}: {}".format(sensor, dataPoint))
                # average value
                store_data /= len(dataPoint)
                # return res containing hourly average for calculating AQI
                res[sensor] = store_data

                # insert this hourly average into database
                c = self.sensorDatabase.cursor()
                c.execute("INSERT INTO sensorDatabase VALUES (:category, :concentration, :date)", 
                        {'category': sensor, 'concentration': store_data, 'date': date})

        self.sensorDatabase.commit()

        # only trim a part of the database not delete every records
        # because validate() method need older record to analyze data
        self.trimDataPoints()

        return res

    def resetDataPoints(self):
        c = self.sensorDataPoints.cursor()
        c.execute("DELETE  FROM sensorDataPoints")
        self.sensorDataPoints.commit()

    def resetDatabase(self):
        c = self.sensorDatabase.cursor()
        c.execute("DELETE  FROM sensorDatabase")
        self.sensorDatabase.commit()

    def trimDataPoints(self):
        c = self.sensorDatabase.cursor()
        c.execute("SELECT COUNT(*) FROM sensorDataPoints")
        # fetchall seem to always return an array of tuple
        recordNum = c.fetchall()[0][0]
        print('in trimDatabase(): numbers of datapoints records: ', recordNum)
        remainRec = NUMBER_OF_PREDICTION_DATA
        if remainRec > recordNum:
            return 0
        
        deletedRec = recordNum - remainRec
        c.execute("DELETE FROM sensorDataPoints\
                ORDER BY date ASC LIMIT :deletedRec",\
                {'deletedRec' : deletedRec})
        self.sensorDatabase.commit()

        return deletedRec

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
    dataStorage = SensorDataStorage()
    print(dataStorage.selectByDate())

    print(PHYSICAL_READ_TIME_INTERVAL)
