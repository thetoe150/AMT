import time
import platform
import IOT
import physical

OS = platform.system()
node_name = "STM32" #for Linux OS
# dataTemp = 0
print("This OS is: ", OS)

vid = 0
init_time = time.time()
counter = 5
cAI = 5
isFire = False
fires = 0

if camPort[1].__len__() != 0:
    vid = cv2.VideoCapture(camPort[1][0])
else:
    print("no camera detected!!!")
    print("try wifi cam...")
    vid = cv2.VideoCapture('http://192.168.50.116:8080/video')



while(True):
    counter, init_time = counting(counter, init_time, 1)
    if counter == cAI:
        cAI = cAI - 2
        if cAI <0: cAI = 5
        if vid != 0:
            ret, frame = vid.read()
            #cv2.imshow('frame', frame)
            res = model(frame)
            res.print()
            result = str(res)
            if result.__contains__("fire"):
                isFire = True
            else: isFire = False    
    if counter <= 0:
        counter = 30
        # if isMicrobitConnected:
        print("trying to read sensor and publish data...")
        try:
            print("Trying to read sersors from all serial ports")
            physicalSensors = physical.Physical()
            publishedJson = physicalSensors.buildJson()
        except Exception as ex:
            print('read sensor fail: ', ex)

        try:
            print("Trying to pushlish")
            clientIOT = IOT.Client()
            clientIOT.publishFeed("nj1.jdata", publishedJson)
        except Exception as ex:
            print('pulish failed: ', ex)


        if isFire:
            fires = fires + 1
        else: fires = 0
        #false positive check: detect fire 2 time in a row
        if fires >= 2:
            print("FIRE!!!!!!!")

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    
  
## After the loop release the cap object
#vid.release()
## Destroy all the windows
#cv2.destroyAllWindows()
