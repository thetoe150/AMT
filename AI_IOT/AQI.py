import json
import requests

airnow_api_key = "86CD0ECF-0480-4C13-9D73-2AC5AA4F8ACD"
iqair_api_key = "fc858e95-4e82-4cab-9349-370009914fb4"

waqi_api_token = "e32c0d793d41c5b11f96f1ae52c54f0e3c584a8b"
# Set the coordinates for Ho Chi Minh City
_HOST = "www.airnowapi.org"
#_ENDPOINT_OBSERVATION_BY_LATLON = "/aq/observation/latLong/current"
_ENDPOINT_OBSERVATION_BY_LATLON = "/aq/data"
_ENDPOINT_FORECAST_BY_LATLON = "/aq/forecast/latLong/current"
latitude = 10.8231
longitude = 106.6297
distanceMiles = 10
bbox = "105,8,107,13"

CATEGORY_NUM = 6

Category = [
    'Good',
    'Moderate',
    'Unhealthy for Sensitive Group',
    'Unhealthy',
    'Very Unhealthy',
    'Hazadous',
    'Hazadous',
]

I = [0, 51, 101, 151, 201, 301, 401]


particle_breakpoints = {
'co' : [0, 4.5, 9.5, 12.5, 15.5, 30.5, 40.5],
'so2' : [0, 36, 76, 186, 305, 605, 805],
'no2' : [0, 54, 101, 361, 650, 1250, 1650],
'pm2_5' : [0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5],
'pm10' : [0, 55, 155, 255, 355, 425, 505]
    
}
class AQI:
    def __init__(self):
        pass

    #@staticmethod
    #def printAirNowAQI():
        #airNowClient = airnowpy.API(apiKey=airnow_api_key)
        #observer = airNowClient.getCurrentObservationByLatLon(longitude= lon, latitude= lat)
        #print("Reporting Area: ", observer[0].reportingArea)
        #print("Date: ", observer[0].timestamp)
        #print("AQI: ", observer[0].aqiValue)
        #print("Category: ", observer[0].category)
        #return observer[0].aqiValue

    @staticmethod
    def calculateAQI(particle_type, pC):
        # Concentration < 0
        if pC < 0:
            print('AQI warning: Invalid AQI input, negative concentration.')
            return -1, -1
    
        breakpoint = []
        for name, bp in particle_breakpoints.items():
            if name == particle_type:
                breakpoint = bp
        
        # No breakpoint info for the current particle
        if len(breakpoint) == 0:
            print('AQI warning: have no breakpoint data for this particle: ', particle_type)
            return -1, -1
        
        low_idx = 0
        category = 'Beyone the AQI - Extremely Hazadous' 
        for i in range(CATEGORY_NUM):
            if pC >= breakpoint[i] and pC < breakpoint[i+1]:
                low_idx = i
                category = Category[i]
                break
        
        high_idx = i + 1
        lerp_factor = (I[high_idx] - I[low_idx]) / (breakpoint[high_idx] - breakpoint[low_idx])
        aqi = (pC - breakpoint[low_idx]) * lerp_factor + I[low_idx]

        aqi = int(round(aqi, 0))

        if aqi > 500:
            aqi = 500

        return aqi, category


    @staticmethod
    def reverseAQI(particle_type, pI):
        if pI < 0:
            print('Negagive concentration!!!')
            return -1

        breakpoint = []
        for name, bp in particle_breakpoints.items():
            if name == particle_type:
                breakpoint = bp

        # No breakpoint info for the current particle
        if len(breakpoint) == 0:
            print('AQI warning: have no breakpoint data for this particle: ', particle_type)
            return -1

        low_idx = 0
        category = 'Beyone the AQI - Extremely Hazadous' 
        for i in range(CATEGORY_NUM):
            if pI >= I[i] and pI < I[i+1]:
                low_idx = i
                break
        
        high_idx = i + 1
        print(low_idx)
        print(high_idx)
        lerp_factor = (breakpoint[high_idx] - breakpoint[low_idx]) / (I[high_idx] - I[low_idx])
        concentration = (pI - I[low_idx]) * lerp_factor + breakpoint[low_idx]

        return concentration


    @staticmethod
    def getJsonFromAirNow(mode, type, lon = longitude, lat = latitude):
        # Validate Arguments
        if (lat < -90 or 90 < lat):
            raise ValueError(
                "lat must be between -90 and 90: " + str(lat))
        if (lon < -180 or 180 < lon):
            raise ValueError(
                "lon must be between -180 and 180: " + str(lon))
        if (distanceMiles < 0):
            raise ValueError(
                "Distance must be a positive integer: " + str(distanceMiles))

        # Send Request and Receive Response
        if mode == 'observation':
            requestUrl = "http://" + _HOST + _ENDPOINT_OBSERVATION_BY_LATLON
            payload = {}
            payload["parameters"] = type
            payload["BBOX"] = bbox
            payload["verbose"] = 0
            payload["includerawconcentrations"] = 0
            # B datatype give both AQI and concentration
            payload["dataType"] = 'B'
            payload["format"] = "application/json"
            payload["API_KEY"] = airnow_api_key

            response = requests.get(requestUrl, params=payload, headers={'Cache-Control': 'no-cache'})

            # if response.history:
                # print("Request was redirected")
                # for resp in response.history:
                    # print(resp.status_code, resp.url)
                # print("Final destination:")
                # print(response.status_code, response.url)
            #else:
                #print("Request was not redirected")
            rawJsonData = json.loads(response.text)
            rawData = rawJsonData[0] 
            print("Date read from AirNow: ", rawData["UTC"])
            print("Ho Chi Minh City")
            return rawData["Parameter"], rawData["Value"], rawData["AQI"]

        elif(mode == 'forecast'):
            requestUrl = "http://" + _HOST + _ENDPOINT_FORECAST_BY_LATLON
            payload = {}
            payload["latitude"] = lat
            payload["longitude"] = lon
            payload["format"] = "application/json"
            payload["API_KEY"] = airnow_api_key
            if (distanceMiles != 0):
                payload["distance"] = distanceMiles

            print(requestUrl)
            response = requests.get(requestUrl, params=payload, headers={'Cache-Control': 'no-cache'}, allow_redirects=False)

            data = json.loads(response.text)
            pretty = json.dumps(data, indent=4)
            return pretty
        else:
            raise ValueError(
                "Mode is be observation or forecast.")

    @staticmethod
    def getJsonFromIQAir():

            requestUrl = "http://api.airvisual.com/v2/nearest_city"
            payload = {}
            payload["key"] = iqair_api_key

            print(type)
            response = requests.get(requestUrl, params=payload, headers={'Cache-Control': 'no-cache'})

            if response.history:
                print("Request was redirected")
                for resp in response.history:
                    print(resp.status_code, resp.url)
                print("Final destination:")
                print(response.status_code, response.url)
            else:
                print("Request was not redirected")

            data = json.loads(response.text)
            pretty = json.dumps(data, indent=4)
            return pretty

    @staticmethod
    def getJsonFromWAQI():

            requestUrl = "https://api.waqi.info/feed/here"
            requestUrlD10 = "https://aqicn.org/station/vietnam/ward-10/h%E1%BA%BBm-108-tr%E1%BA%A7n-v%C4%83n-quang"
            payload = {}
            payload["token"] = waqi_api_token

            response = requests.get(requestUrl, params=payload, headers={'Cache-Control': 'no-cache'})

            if response.history:
                print("Request was redirected")
                for resp in response.history:
                    print(resp.status_code, resp.url)
                print("Final destination:")
                print(response.status_code, response.url)
            else:
                print("Request was not redirected")

            data = json.loads(response.text)
            pretty = json.dumps(data, indent=4)

            print(pretty)

            return pretty
    
if __name__ == '__main__':
    # print(AQI.calculateAQI("no2", 5800))

    #print(AQI.getJsonFromAirNow('observation','OZONE,PM25,PM10,CO,NO2,SO2'))
    #print(AQI.getJsonFromAirNow('forecast','OZONE,PM25,PM10,CO,NO2,SO2'))

    #print(AQI.getJsonFromAirNow('observation','OZONE,PM25,PM10,CO,NO2,SO2'))
    #print(AQI.getJsonFromAirNow())
    #print(AQI.getJsonFromIQAir())
    #print(AQI.getJsonFromWAQI())


    print(AQI.reverseAQI('pm2_5', 57))
