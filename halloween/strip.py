import fcntl
import array
from halloween.colors import Color
import time
import requests
BLACK = Color().BLACK


class Strip(object):

    def __init__(self, length, spi='/dev/spidev0.0'):
        '''
        initialize strip with length pixels and setup SPI interface
        '''
        #spi = "/tmp/strip_test"
        self.spidev = open(spi, "wb")
        #set the spi frequency to 400kbps
        fcntl.ioctl(self.spidev, 0x40046b04, array.array('L', [400000]))
        self.length = length
        self.pixels = []
        self.brightness = 50
        for i in range(length):
            pixel = Pixel()
            self.pixels.append(pixel)

    def set_pixel(self, pixel, color=None, state=None):
        '''
        set singel pixel to color and state
        '''
        if color:
            self.pixels[pixel].set_color(self.brightness_adj(color))
        if state:
            self.pixels[pixel].set_state(state)

    def get_pixel(self, pixel):
        '''
        get singel pixel color and state
        '''
        color = self.pixels[pixel].rgb
        return color

    def brightness_adj(self, color):
        c = bytearray([0, 0, 0])
        c[0] = int(self.brightness * color[0] / 100)
        c[1] = int(self.brightness * color[1] / 100)
        c[2] = int(self.brightness * color[2] / 100)
        return c


    def show(self):
        '''
        show the strip (pipe the data to the strip leds)
        '''
        msg = bytearray()
        for _ in self.pixels:
            msg.extend(_.rgb)
        self.spidev.write(msg)
        self.spidev.flush()

    def all_off(self):
        '''
        fill all pixels with 000 to turn them off
        '''
        msg = bytearray()
        for _ in self.pixels:
            msg.extend(BLACK)
        self.spidev.write(msg)
        self.spidev.flush()


class ArduinoStrip(Strip):
    def __init__(self, x=3, y=3, host=None):
        """
        initialize ArduinoStrip
        """
        self.pixels = []
        self.brightness = 100
        self.host = host
        self.length = x * y
        for pixx in range(x):
            if pixx % 2 == 0:
                for pixy in range(y):
                    pixel = Pixel(pixx, pixy)
                    self.pixels.append(pixel)
            else:
                for pixy in reversed(range(y)):
                    pixel = Pixel(pixx, pixy)
                    self.pixels.append(pixel)

    def show(self):
        '''
        show the strip (pipe the data to the strip leds)
        '''
        for pixel in self.pixels:
            payload = {
                "x": pixel.x,
                "y": pixel.y,
                "red": pixel.red,
                "green": pixel.green,
                "blue": pixel.blue
            }
            try:
                ret = requests.post(self.host, data=payload)
            except:
                print("Exception raised on request. sleeping for 20 seconds")
                time.sleep(20)

    def all_off(self):
        '''
        fill all pixels with 000 to turn them off
        '''
        for pixel in self.pixels:
            payload = {
                "x": pixel.x,
                "y": pixel.y,
                "red": 0,
                "green": 0,
                "blue": 0
            }
            try:
                ret = requests.post(self.host, data=payload)
            except:
                print("Exception raised on request. sleeping for 20 seconds")
                time.sleep(20)


class Pixel(object):

    def __init__(self, x=0, y=0):
        self.red = 0
        self.green = 0
        self.blue = 0
        self.x = x
        self.y = y
        self.rgb = bytearray(3)

    def latch(self):
        self.rgb[0] = self.red
        self.rgb[1] = self.green
        self.rgb[2] = self.blue

    def set_color(self, color):
        self.rgb = color
        self.red = int(self.rgb[0])
        self.green  = int(self.rgb[1])
        self.blue = int(self.rgb[2])
