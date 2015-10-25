import fcntl
import array
from halloween.colors import BLACK

class Strip(object):

    def __init__(self, lenght, spi='/dev/spidev0.0'):
        '''
        initialize strip with length pixels and setup SPI interface
        '''
        spidev = open(spi, "wb")
        #set the spi frequency to 400kbps
        #fcntl.ioctl(spidev, 0x40046b04, array.array('L', [400000]))
        self.pixels = []
        for i in range(lenght):
            pixel = Pixel()
            self.pixels.append(pixel)

    def set_pixel(self, pixel, color=None, state=None):
        '''
        set singel pixel to color and state
        '''
        if color:
            self.pixels[pixel].set_color(color)
        if state:
            self.pixels[pixel].set_state(state)

    def show(self):
        '''
        show the strip (pipe the data to the strip leds)
        '''
        msg = bytearray()
        for _ in self.pixels:
            msg.extend(_.rgb)
        spidev.write(msg)
        spidev.flush()

    def all_off(self):
        '''
        fill all pixels with 000 to turn them off
        '''
        msg = bytearray()
        for _ in self.pixels:
            msg.extend(colors.BLACK)
        spidev.write(msg)
        spidev.flush()


class Pixel(object):

    def __init__(self):
        self.red = 0
        self.green = 0
        self.blue = 0
        self.rgb = bytearray(3)

    def set_color(self, color):
        self.rgb = color
