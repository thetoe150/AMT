PHYSICAL_READ_TIME_INTERVAL = 10 
NUMBER_OF_DATAPOINTS = 6

#NUMBER_OF_PREDICTION_DATA should be > NUMBER_OF_DATAPOINTS
# NUMBER_OF_PREDICTION_DATA should be > 70 for 
# the ARMA model to not complain
NUMBER_FOR_PREDICTION_DATA = 20
NUMBER_FOR_PREDICTION_AQI = 20

CO_THRESHOLD = 60
TEM_THRESHOLD = 60

VALIDATING_THRESHOLD = {
    "temperature" : 5,
    "humidity" : 10,
    "co" : 5,
    "co2": 15,
    "so2": 5,
    "no2": 5,
    "pm2_5": 10,
    "pm10":  10
}
