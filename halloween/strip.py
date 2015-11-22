import fcntl
import array
from halloween.colors import Color
import time
BLACK = Color().BLACK

class Strip(object):

    def __init__(self, length, spi='/dev/spidev0.0'):
        '''
        initialize strip with length pixels and setup SPI interface
        '''
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
        get singel pixel to color and state
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


class Pixel(object):

    def __init__(self):
        self.red = 0
        self.green = 0
        self.blue = 0
        self.rgb = bytearray(3)

    def latch(self):
        self.rgb[0] = self.red
        self.rgb[1] = self.green
        self.rgb[2] = self.blue

    def set_color(self, color):
        self.rgb = color
