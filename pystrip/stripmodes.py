from threading import Thread
import colorsys
import json
import logging
import math
import random
import time
from pystrip.colors import Color
from pystrip.config import load_config

LOG = logging.getLogger(__name__)


def rand_sleep(max_sleep=3):
    time.sleep(random.randint(1, max_sleep))


class StripModes(Thread):

    def __init__(self, strip, stop, lock, params):
        super(StripModes, self).__init__()
        self.daemon = True
        self.strip = strip
        self.stop = stop
        self.lock = lock
        self.name = 'StripMode'
        self.params = params


class OneColor(StripModes):
    MODE = 'OneColor'

    def run(self):
        LOG.debug("Running one Color mode")
        return


class Halloween(StripModes):
    MODE = 'Halloween'

    def run(self):
        LOG.debug("Running Halloween Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        crange = [
            Color().AQUAMARINE,
            Color().BROWN,
            Color().CYAN,
            Color().DARKVIOLET,
            Color().RED,
            Color().DARKGREEN,
            Color().DARKBLUE,
            Color().YELLOW,
            Color().BLACK]
        while not self.stop.is_set():
            i = random.randint(0, 9)
            if i != random.choice(
                    [0, 9, 1, 8, 2, 7, 3, 6, 4, 5, 6, 4, 7, 3, 8, 2, 9, 1, 0]):
                color = random.choice(crange[:-1])
                for _ in '0110010110110011010101110111':
                    self.lock.acquire()
                    if _ == random.choice(['0', '1']):
                        self.strip.set_pixel(i, color=Color().BLACK)
                    else:
                        self.strip.set_pixel(i, color=color)
                    self.strip.show()
                    self.lock.release()
                    time.sleep(0.05)
            else:
                self.lock.acquire()
                if self.strip.pixels[i].rgb != Color().BLACK:
                    self.strip.set_pixel(i, color=Color().BLACK)
                else:
                    self.strip.set_pixel(i, color=random.choice(crange))
                self.strip.show()
                self.lock.release()
            time.sleep(random.randint(2, 5) * 0.5)
        LOG.debug("Halloween Mode Stopped")
        self.strip.all_off()


class Helloween2(StripModes):
    MODE = 'Helloween2'

    def __init__(self, strip, stop, lock):
        super(Helloween2, self).__init__(strip, stop, lock)
        self.pixel_per_pumpkin = 3
        self.pumpkins = []
        self.pumpkins = [
            self.strip.pixels[
                _:_+self.pixel_per_pumpkin] for _ in range(
                0, self.strip.length, self.pixel_per_pumpkin)
        ]

    def run(self):
        LOG.debug("Starting Helloween2")
        LOG.debug("Stip length : {}".format(self.strip.length))
        crange = [
            Color().AQUAMARINE,
            Color().BROWN,
            Color().CYAN,
            Color().DARKVIOLET,
            Color().RED,
            Color().DARKGREEN,
            Color().DARKBLUE,
            Color().YELLOW]
        while not self.stop.is_set():
            pumkin = random.choice(self.pumpkins)
            color = random.choice(crange[:-1])
            for _ in '0110010110110011010101110111':
                self.lock.acquire()
                if _ == random.choice(['0', '1']):
                    for pixel in pumkin:
                        pixel.set_color(color=Color().BLACK)
                else:
                    for pixel in pumkin:
                        pixel.set_color(color=color)
                self.strip.show()
                self.lock.release()
                time.sleep(0.05)
            time.sleep(random.randint(2, 5) * 0.5)

        LOG.debug("Helloween2 Mode Stopped")
        self.strip.all_off()


class Disco(StripModes):
    MODE = 'Disco'

    def run(self):
        LOG.debug("Starting Disco Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        while not self.stop.is_set():
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=Color().RED)
            self.strip.show()
            self.lock.release()
            time.sleep(1)
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=Color().GREEN)
            self.strip.show()
            self.lock.release()
            time.sleep(1)
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=Color().BLUE)
            self.strip.show()
            self.lock.release()
            time.sleep(1)
        LOG.debug("Disco Mode Stopped")
        self.strip.all_off()


class Smoothie(StripModes):
    MODE = 'Smoothie'

    def run(self):
        LOG.debug("Starting Smoothie Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        while not self.stop.is_set():
            color = bytearray([0, 0, 0])
            for i in range(100):
                color[0] = i
                self.lock.acquire()
                for p in range(self.strip.length):
                    self.strip.set_pixel(p, color=color)
                self.strip.show()
                self.lock.release()
                time.sleep(0.02)
            for i in reversed(range(100)):
                color[0] = i
                self.lock.acquire()
                for p in range(self.strip.length):
                    self.strip.set_pixel(p, color=color)
                self.strip.show()
                self.lock.release()
                time.sleep(0.02)
        LOG.debug("Smoothie Stopped")
        self.strip.all_off()


class Washer(StripModes):
    MODE = "Washer"

    def run(self):
        LOG.debug("Starting Washer")
        i = 0
        color = bytearray([0, 0, 0])
        while not self.stop.is_set():
            i += 1
            alpha = 0.00001 * i
            alpha = 0.01 * i
            if alpha >= 360:
                i = 0
            val_red = self.alpha_calc(alpha, 0)
            val_green = self.alpha_calc(alpha, 90)
            val_blue = self.alpha_calc(alpha, 180)
            color[0] = val_red
            color[1] = val_green
            color[2] = val_blue
            for p in range(self.strip.length):
                self.strip.set_pixel(p, color=color)
            self.strip.show()
            time.sleep(0.3)
        LOG.debug("Washer Stopped")
        self.strip.all_off()

    @staticmethod
    def alpha_calc(alpha, phase):
        fun = math.sin(alpha + phase)
        fun = fun * 255
        value = int(fun)
        if value < 0:
            value = 0
        return value


class Firelane(StripModes):
    MODE = 'Firelane'

    def run(self):
        LOG.debug("Starting Firelane")
        crange = [
            Color().AQUAMARINE,
            Color().BROWN,
            Color().CYAN,
            Color().DARKVIOLET,
            Color().RED,
            Color().DARKGREEN,
            Color().DARKBLUE,
            Color().YELLOW]
        round = 0
        pcol = random.choice(crange)
        while not self.stop.is_set():
            round += 1
            if round == 51:
                round = 1
                pcol = random.choice(crange)
            for p in range(self.strip.length):
                if p == round:
                    self.strip.set_pixel(p, color=Color().BLACK)
                else:
                    self.strip.set_pixel(p, color=pcol)
                self.strip.show()
        LOG.debug("Firelane Stopped")
        self.strip.all_off()


class Mover(StripModes):
    MODE = 'Mover'

    def run(self):
        LOG.debug("Starting Mover")
        color = Color()
        f = [val for attr, val in color.__dict__.items()]
        while not self.stop.is_set():
            for p in range(self.strip.length):
                color = random.choice(f)
                self.strip.set_pixel(p, color=color)
            self.strip.show()
            time.sleep(1)
        LOG.debug("Mover Stopped")
        self.strip.all_off()


class Mycolor(StripModes):
    MODE = 'MyColor'

    def run(self):
        def check(color, avr, dif):
            c = 0 + color
            if c < avr:
                c += dif
            else:
                c -= dif
            if c < 0:
                c = random.randint(0, 255)
            if c > 255:
                c = random.randint(0, 255)
            return c

        neighbours = {
            0: [1, 5],
            1: [0, 2, 3, 4],
            2: [1, 3],
            3: [2, 4, 8],
            4: [1, 3, 5, 7],
            5: [0, 4, 6],
            6: [5, 7],
            7: [6, 4, 8],
            8: [3, 7]
        }
        LOG.debug("Starting MyColor")
        for led in range(self.strip.length):
            rred = random.randint(0, 255)
            rgreen = random.randint(0, 255)
            rblue = random.randint(0, 255)
            color = bytearray([rred, rgreen, rblue])
            self.strip.set_pixel(led, color=color)
        self.strip.show()
        led = 0
        while not self.stop.is_set():
            for led in range(self.strip.length):
                ncount = len(neighbours[led])
                total_red = 0
                total_green = 0
                total_blue = 0
                for pix in neighbours[led]:
                    ncolor = self.strip.get_pixel(pix)
                    total_red += ncolor[0]
                    total_green += ncolor[1]
                    total_blue += ncolor[2]

                avr_red = total_red / ncount
                avr_green = total_green / ncount
                avr_blue = total_blue / ncount
                dif_red = color[0] - avr_red
                dif_green = color[1] - avr_green
                dif_blue = color[2] - avr_blue

                color[0] = check(color[0], avr_red, dif_red)
                color[1] = check(color[1], avr_green, dif_green)
                color[2] = check(color[2], avr_blue, dif_blue)

                self.strip.set_pixel(led, color=color)
            self.strip.show()
            time.sleep(1)
        LOG.debug("MyColor Stopped")
        self.strip.all_off()


class Game(StripModes):
    '''
    Tic-Tac-Toe class.
    This class holds the user interaction, and game logic
    '''
    MODE = 'TICTACTOE'

    def __init__(self, strip, stop, lock):
        super(Game, self).__init__(strip, stop, lock)


def hls_to_bytearray(h, l, s):
    hsl = colorsys.hls_to_rgb(h/360, l, s)
    r, g, b = (int(hsl[0] * 255), int(hsl[1] * 255), int(hsl[2] * 255))
    color = [r, g, b]
    return bytearray(color)

def color_cycle(h ,l ,s):
    # TODO : check if 70 > l*100 
    up_range = list(range(int(l*100), 70))
    down_range = reversed(up_range)
    up_range.extend(down_range)
    for i in up_range:
        yield hls_to_bytearray(h, i/100, s)

class Clear(StripModes):
    '''
    clear weather conditions
    '''
    MODE = 'Clear'

    def run(self):
        LOG.debug("Clear Weather Conditions started")
        strip_range = range(self.strip.length)
        while not self.stop.is_set():
            color = color_cycle(60, 0.5, 1)   # yellow
            for led in strip_range:
                self.strip.set_pixel(led, hls_to_bytearray(60, 0.5, 1))
            leds = random.sample(strip_range, 3)
            try:
                for c in color:
                    for led in leds:
                        self.strip.set_pixel(led, c)
                    self.strip.show()
            except StopIteration:
                pass

        LOG.debug("Stopped Clear Weather Conditions")
        self.strip.all_off()


class Rainy(StripModes):
    '''
    Weather class for rainy days
    '''
    MODE = 'rainy'

    def run(self):
        LOG.debug("Rany  Weather Conditions started")
        strip_range = range(self.strip.length)
        while not self.stop.is_set():
            color = color_cycle(240, 0.3, 1)   # Dark Blueich
            for led in strip_range:
                self.strip.set_pixel(led, hls_to_bytearray(240, 0.3, 1))
            leds = random.sample(strip_range, 3)
            try:
                for c in color:
                    for led in leds:
                        self.strip.set_pixel(led, c)
                    self.strip.show()
            except StopIteration:
                pass

        LOG.debug("Stopped Rainy  Weather Conditions")
        self.strip.all_off()


class Drops(StripModes):
    '''
    Teardrops mode
    '''
    MODE = 'Teardrops'

    def run(self):
        LOG.debug("Teardrops started.")
        '''
        2 3 8
        1 4 7
        0 5 6
        '''
        cfg = load_config()
        if 'speed' in self.params:
            speed = int(self.params['speed'])
        else:
            speed = None
        if 'hue' in self.params:
            hue = int(self.params['hue'])
            color = hls_to_bytearray(int(self.params['hue']), 0.5, 1)
        else:
            hue = 241
            color = hls_to_bytearray(241, 0.5, 1)
        drops = {}
        for option in cfg.options("drops"):
            drops[option] = json.loads(cfg.get("drops", option))
            LOG.debug(option)
            LOG.debug(type(drops[option]))
        LOG.debug(drops)
        strip_range = range(self.strip.length)
        while not self.stop.is_set():
            time.sleep(1)
            for led in strip_range:
                self.strip.set_pixel(led, color)
            drop = random.choice(range(1, len(drops) + 1))
            for pixel in drops[str(drop)]:
                self.strip.set_pixel(pixel, hls_to_bytearray(hue, 0.59, 1))
                self.strip.show()
                self.strip.set_pixel(pixel, hls_to_bytearray(hue, 0.5, 1))
            self.strip.show()
            if speed:
                time.sleep(speed * 0.01)

        LOG.debug("Stopped Teardrops")
        self.strip.all_off()
