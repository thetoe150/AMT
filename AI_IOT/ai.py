import cv2
import torch
import json
import IOT
# import board,busio
# import numpy as np
# import adafruit_mlx90640
# import matplotlib.pyplot as plt

class AICam:
    def __init__(self):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
        self.isFire = False

        self.camPorts = []
        self.getPorts()
        # initCam() have to be called after getPort()
        self.camCaps = []
        self.initCams()

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
            print("try wifi cam at  http://192.168.50.116:8080/video")
            vid = cv2.VideoCapture('http://192.168.50.116:8080/video')
    
    def readCams(self):
        port_idx = 0
        for cam in self.camCaps:
            is_reading, frame = cam.read()
            if not is_reading:
                print('cannot read frame at cam', cam)
                break

            cv2.imshow('Tesing cam' + str(self.camPorts[port_idx]), frame)
            # magic if statement - don't delete
            if cv2.waitKey(1) == ord('q'):
                break

            res = self.model(frame)
            res.print()
            # Data
            print('\n', res.xyxy[0])  # print img1 predictions

            result = str(res)
            if result.__contains__("fire"):
                print('Fire detected at port: ', self.camPorts[port_idx])
                self.isFire = True

            port_idx += 1

    def processImages(self):
        # TODO: process camera images and inferred camera images and ouput isFire
        pass
#         print("Initializing MLX90640")
#         i2c = busio.I2C(board.SCL, board.SDA, frequency=800000) # setup I2C
#         mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
#         mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh rate
#         mlx_shape = (24,32)
#         print("Initialized")

#         fire_threshold = 90 # temperature threshold for fire detection

#         # setup the figure for plotting
#         plt.ion() # enables interactive plotting
#         fig,ax = plt.subplots(figsize=(12,7))
#         therm1 = ax.imshow(np.zeros(mlx_shape),vmin=0,vmax=60) #start plot with zeros
#         cbar = fig.colorbar(therm1) # setup colorbar for temps
#         cbar.set_label('Temperature [$^{\circ}$C]',fontsize=14) # colorbar label

#         frame = np.zeros((24*32,)) # setup array for storing all 768 temperatures
#         # t_array = []
#             # t1 = time.monotonic()
#         try:
#             mlx.getFrame(frame) # read MLX temperatures into frame var
#             data_array = (np.reshape(frame,mlx_shape)) # reshape to 24x32
#             therm1.set_data(np.fliplr(data_array)) # flip left to right
#             therm1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
#             cbar.update_normal(therm1) # update colorbar range

#             fire_count = np.sum(data_array > fire_threshold) # count the number of pixels above the fire threshold
#             if (fire_count > (0.5 * mlx_shape[0] * mlx_shape[1]) and self.isFire): # if more than half of the pixels exceed the threshold
#                 self.isFire = True
#             else:
#                 self.isFire = False

#             plt.title(f"Max Temp: {np.max(data_array):.1f}C")
#             plt.pause(0.001) # required
#             #fig.savefig('mlx90640_test_fliplr.png',dpi=300,facecolor='#FCFCFC', bbox_inches='tight') # comment out to speed up
#             # t_array.append(time.monotonic()-t1)
#             # print('Sample Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))
#         except ValueError:
#             print('Error reading thermal camera')

    def buildJson(self):
        # check if any data have been read
        if not self.camCaps:
            print('There is no camera data to build Json for fire detection')
            return ''
        
        jsonData = '{"isFire": '
        if self.isFire:
            jsonData += 'true}'
        else:
            jsonData += 'false}'


        # check to see whether the string is correct in json format
        parsed = json.loads(jsonData)
        print(json.dumps(parsed, indent=4))

        return jsonData

    def publishData(self):
        json = self.buildJson()
        if json != '':
            self.camClient.publishFeed("nj1.isfire", json)


if __name__ == '__main__':
    fireDetector = AICam()
    while True:
        fireDetector.readCams()
        fireDetector.processImages()
        fireDetector.publishData()
