import matplotlib.pyplot as plt
import numpy as np
from time import time, sleep
import board,busio
import adafruit_mlx90640


MLX_SHAPE = (24,32)

class ThermoCam:
    def __init__(self, isVisualize):
        ######## Set up I2C communication and MLX instance ##########
        self.isVisualize = isVisualize
        self.i2c = None
        self.mlx = None
        self.initInferedCam()

        ########## Set up plot ##########
        if self.isVisualize:
            self.therm1 = None
            self.cbar = None
            self.initInferedImage()

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
        frame = np.zeros((24*32,)) # setup array for storing all 768 temperatures
        # t_array = []
            # t1 = time.monotonic()
        try:
            self.mlx.getFrame(frame) # read MLX temperatures into frame var
            data_array = (np.reshape(frame, MLX_SHAPE)) # reshape to 24x32
            
            # Draw image if enabe visualize in the constructor
            if self.isVisualize:
                self.therm1.set_data(np.fliplr(data_array)) # flip left to right
                self.therm1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
                self.cbar.update_normal(self.therm1) # update colorbar range

            # detect fire

            plt.title(f"Max Temp: {np.max(data_array):.1f}C")
            plt.pause(0.001) # required
            #fig.savefig('mlx90640_test_fliplr.png',dpi=300,facecolor='#FCFCFC', bbox_inches='tight') # comment out to speed up
            # t_array.append(time.monotonic()-t1)
            # print('Sample Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))
        except ValueError:
            print('Error reading thermal camera')



if __name__ == '__main__':
    thermo_cam = ThermoCam(True)
    while True:
        thermo_cam.readInferedCam()
        sleep(1)
