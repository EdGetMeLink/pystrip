import time
import array
import fcntl
import random
import colors
import signal
import sys

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    msg = bytearray(255)
    spidev.write(msg)
    spidev.flush()
    sys.exit(0)

def main():
    spidev = file("/dev/spidev0.0", "wb")
    #byte array to store the Red, Green and Blue values
    crange = [colors.RED, colors.GREEN, colors.BLUE]
    rgb=bytearray(3)
    #set the spi frequency to 400kbps
    fcntl.ioctl(spidev, 0x40046b04, array.array('L', [400000]))

    while True :
        #use your own colors here
        rgb[0] = random.randrange(255)
        rgb[1] = random.randrange(255)
        rgb[2] = random.randrange(255)
        rbg2 = colors.RED
        spidev.write(random.choice(crange) + random.choice(crange))
        spidev.flush()
        time.sleep(.2)
        print("flusch to 0")
        rgb[0] = 0
        rgb[1] = 0
        rgb[2] = 0
        spidev.write(rgb + rgb)
        spidev.flush()


class Strip(object):

    def __init__(self, lenght):
        self.pixels = []
        for i in range(lenght):
            pixel = Pixel()
            self.pixels.append(pixel)

    def set_pixel(self, pixel, color=None, state=None):
        if color:
            self.pixels[pixel].set_color(color)
        if state:
            self.pixels[pixel].set_state(state)

    def show(self):
        msg = bytearray()
        for _ in self.pixels:
            msg.extend(_.rgb)
        print('\033[92m %s' % [c for c in msg])
        spidev.write(msg)
        spidev.flush()

    def all_off(self):
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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    crange = [colors.AQUAMARINE, colors.BROWN, colors.CYAN, colors.DARKVIOLET, colors.RED, colors.DARKGREEN, colors.DARKBLUE, colors.YELLOW, colors.BLACK]

    spidev = file("/dev/spidev0.0", "wb")
    #set the spi frequency to 400kbps
    fcntl.ioctl(spidev, 0x40046b04, array.array('L', [400000]))
    print("initialize")
    strip = Strip(10)
    for color in crange:
        for i in range(10):
            strip.set_pixel(i, color=color)
        strip.show()
        time.sleep(0.3)
    print("part 2")
    for idx, color in enumerate(crange[:-1]):
        print("Color : %s" % idx)
        for line in range(10):
            for i in range(10):
                strip.set_pixel(i, color=color)
            strip.set_pixel(line, color=colors.BLACK)
            strip.show()
            time.sleep(0.3)

    print("go on")
    strip = Strip(10)
    while True:
        i = random.randint(0, 9)
        if i != random.choice([0, 9, 1, 8, 2, 7, 3, 6, 4, 5, 6, 4, 7, 3, 8, 2, 9, 1, 0]):
            color = random.choice(crange[:-1])
            for _ in '0110010110110011010101110111':
                if _ == random.choice(['0', '1']):
                    strip.set_pixel(i, color=colors.BLACK)
                else:
                    strip.set_pixel(i, color=color)
                strip.show()
                time.sleep(0.05)
        else:
            if strip.pixels[i].rgb != colors.BLACK:
                strip.set_pixel(i, color=colors.BLACK)
            else:
                strip.set_pixel(i, color=random.choice(crange))
            strip.show()
        time.sleep(random.randint(2, 5) * 0.5)
