
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

    @staticmethod
    def calculateAQI(particle_type, pC):
        breakpoint = []
        for name, bp in particle_breakpoints.items():
            if name == particle_type:
                breakpoint = bp
        
        if len(breakpoint) == 0:
            print('have no breakpoint data for this particle')
            return -1, -1
        
        low_idx = 0
        category = 'concentration is out of breakpoint bound' 
        for i in range(CATEGORY_NUM):
            if pC >= breakpoint[i] and pC < breakpoint[i+1]:
                low_idx = i
                print(low_idx)
                category = Category[i]
                break
        
        high_idx = i + 1
        lerp_factor = (I[high_idx] - I[low_idx]) / (breakpoint[high_idx] - breakpoint[low_idx])
        aqi = (pC - breakpoint[low_idx]) * lerp_factor + I[low_idx]
        if aqi > 500:
            aqi = 500

        return aqi, category
    


#print(AQI.calculateAQI("no2", 200))
