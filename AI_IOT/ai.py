import cv2
import torch
import IOT
#import board,busio
import numpy as np
#import adafruit_mlx90640
import matplotlib.pyplot as plt

import log

from time import time, sleep

FIRE_THRESHOLD = 90 # temperature threshold for fire detection
MLX_SHAPE = (24,32)

class AICam:
    def __init__(self, debug = False):
        self.isDebug = debug
        ########### Set up log #################
        if self.isDebug:
            self.log = log.setupLogger('ai_log','log/ai.log')

        self.isFireAI = False
        self.isFireThermal = False
        self.alertLevel = "Low"
        ######## Set up AI model ########

        self.model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
        ######## Set up ports and camera Capture instance for normal camera ########
        self.camPorts = []
        self.getPorts()
        # initCam() have to be called after getPort()
        self.camCaps = []
        self.initCams()

        ######## Set up I2C communication and MLX instance ##########
        self.i2c = None
        self.mlx = None
        #self.initInferedCam()

        ######## Set up plot ##########
        if self.isDebug:
            self.therm1 = None
            self.cbar = None
            self.initInferedImage()

        ######## Init adafruit instance for camera component ########
        self.camClient = IOT.Client()


    def getPorts(self):
        """
        Test the ports and returns a tuple with the available ports and the ones that are working.
        """
        non_working_ports = []
        dev_port = 0

        while len(non_working_ports) < 3:  # if there are more than 4 non working ports stop the testing.
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                non_working_ports.append(dev_port)
                print("Port %s is not working." % dev_port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" % (dev_port, h, w))
                    self.camPorts.append(dev_port)
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." % (dev_port, h, w))
            dev_port += 1
    
    def initCams(self):
        if self.camPorts.__len__() != 0:
            for cam in self.camPorts:
                self.camCaps.append(cv2.VideoCapture(cam))
        else:
            print("no camera detected!!!")
            #print("try wifi cam at  http://192.168.50.116:8080/video")
            #vid = cv2.VideoCapture('http://192.168.50.116:8080/video')
            
    def readCams(self):
        # WARNING: using for loop to iterate through the list of camture objects
                # significantly reduce speed

        #port_idx = 0
        #for cam in self.camCaps:
            #is_reading, frame = cam.read()
            #if not is_reading:
                #print('cannot read frame at cam', cam)
                #break

            #if self.isDebug:
                #cv2.imshow('Tesing cam' + str(self.camPorts[port_idx]), frame)
            ## magic if statement - don't delete
            #if cv2.waitKey(1) == ord('q'):
                #break

            #res = self.model(frame)
            #res.print()
            ## Data
            #print('\n', res.xyxy[0])  # print img1 predictions

            #result = str(res)
            #if result.__contains__("fire"):
                #print('Fire detected at port: ', self.camPorts[port_idx])
                #self.isFireAI = True
            #else:
                #self.isFireAI = False

            #port_idx += 1

        cam = self.camCaps[0]
        is_reading, frame = cam.read()
        if not is_reading:
            print('cannot read frame at cam', cam)

        res = self.model(frame)
        predictions = res.pred[0]
        boxes = predictions[:, :4] # x1, y1, x2, y2
        res.print()

        #predict_image = model(image)
#im_rgb = cv2.cvtColor(predict_image.imgs[0], cv2.COLOR_BGR2RGB) # Because of OpenCV reading images as BGR
#cv2_imshow(im_rgb)

        if self.isDebug:
            #image = cv2.rectangle(image, start_point, end_point, color, thickness)
            image = cv2.rectangle(frame, tuple(boxes[0,1]), tuple(boxes[2,3]), (255,0,0), 2)
            cv2.imshow('Debug cam', image)
        # magic if statement - don't delete
        if cv2.waitKey(1) == ord('q'):
            pass

        # Data
        # self.log.info(res.xyxy[0])  # print img1 predictions

        result = str(res)
        if result.__contains__("fire"):

            if self.isDebug:
                self.log.info('Fire detected !')

            self.isFireAI = True
        else:
            self.isFireAI = False

    def initInferedCam(self):
        print("Initializing MLX90640")
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=800000) # setup I2C
        self.mlx = adafruit_mlx90640.MLX90640(self.i2c) # begin MLX90640 with I2C comm
        self.mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh rate
        print("Initialized")
    
    def initInferedImage(self):
        # setup the figure for plotting
        plt.ion() # enables interactive plotting
        fig,ax = plt.subplots(figsize=(12,7))
        self.therm1 = ax.imshow(np.zeros(MLX_SHAPE),vmin=0,vmax=60) #start plot with zeros
        self.cbar = fig.colorbar(self.therm1) # setup colorbar for temps
        self.cbar.set_label('Temperature [$^{\circ}$C]',fontsize=14) # colorbar label

    def readInferedCam(self):
        self.log.info("reading infered cam")
        frame = np.zeros((24*32,)) # setup array for storing all 768 temperatures
        # t_array = []
            # t1 = time.monotonic()
        try:
            self.mlx.getFrame(frame) # read MLX temperatures into frame var
            data_array = (np.reshape(frame, MLX_SHAPE)) # reshape to 24x32
            
            # Draw image if enabe visualize in the constructor
            if self.isDebug:
                self.therm1.set_data(np.fliplr(data_array)) # flip left to right
                self.therm1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
                self.cbar.update_normal(self.therm1) # update colorbar range

            # detect fire
#             fire_count = np.sum(data_array > FIRE_THRESHOLD) # count the number of pixels above the fire threshold
            max_temp = np.max(data_array)
            if (max_temp >= 80): # if more than half of the pixels exceed the threshold
                self.isFireThermal = True
            else:
                self.isFireThermal = False

            plt.title(f"Max Temp: {np.max(data_array):.1f}C")
            plt.pause(0.001) # required
            #fig.savefig('mlx90640_test_fliplr.png',dpi=300,facecolor='#FCFCFC', bbox_inches='tight') # comment out to speed up
            # t_array.append(time.monotonic()-t1)
            # print('Sample Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))
        except ValueError:
            self.log.error('Error reading isFireThermal camera')
    
    def integrateResult(self):
        if not self.isFireThermal and not self.isFireAI:
            self.alertLevel = "None"
        elif self.isFireThermal and not self.isFireAI:
            self.alertLevel = "Low"
        elif not self.isFireThermal and self.isFireAI:
            self.alertLevel = "Low"
        elif self.isFireThermal and self.isFireAI:
            self.alertLevel = "High"
    
    def setGlobalDetectVal(self):
        global isFireCam
        isFireCam = self.alertLevel

    def publishData(self, value):
        if value != '':
            self.camClient.publishFeed("nj1.isfire", value)

            if self.isDebug:
                self.log('Publishing fire level: {}'.format(value))

if __name__ == '__main__':
    fireDetector = AICam(True)
    while True:
        fireDetector.readCams()
        #fireDetector.readInferedCam()

        #fireDetector.integrateResult()
        fireDetector.setGlobalDetectVal()