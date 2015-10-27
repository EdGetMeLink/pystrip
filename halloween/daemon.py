import logging
import logging.handlers
import random
import colors
import sys
import time
import json

from threading import Thread, Event, Timer, Lock
from halloween.strip import Strip

LOG = logging.getLogger(__name__)


def setup_logging():
    LOG_FILE = "halloween.log"
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    formatter = (
        '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
    #file_handler = logging.handlers.RotatingFileHandler(LOG_FILE,
    #        maxBytes=1024*1024,
    #        backupCount=5)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    #root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


class Runner(Thread):

    def __init__(self, queue, strip_length):
        super(Runner, self).__init__()
        self.daemon = True
        self.name = "Main Runner"
        self.queue = queue
        self.stop_event = Event()
        self.strip_mode = 'Halloween'
        self.strip_state = 'off'
        self.thread = None
        self.lock = Lock()
        self.strip = Strip(strip_length)
        LOG.debug("Initialized Daemon")

    def run(self):

        exitflag = False
        LOG.debug("Starting Timer")
        self.refresh_timer = Timer(0.01, self.refresh_strip)
        self.refresh_timer.start()
        while not exitflag:
            try:
                self.data = self.queue.get()
                LOG.debug("Data received %s" % self.data)
                self.decode()
            except (Exception, KeyboardInterrupt, SystemExit) as e:
                LOG.exception('Exception : {}'.format(e))
                exitflag = True
        self.refresh_timer.cancel()

    def decode(self):
        try:
            self.data = json.loads(self.data)
            self.data = self.data['strip']
            self.strip_state = self.data.get('state', self.strip_state)
            self.strip_mode = self.data.get('mode', self.strip_mode)
            if self.strip_state == 'on':
                self.stop_event.set()
                if self.thread:
                    LOG.debug("Waiting for old thread to stop")
                    self.thread.join()
                    LOG.debug("Thread stopped")
                self.stop_event.clear()
                for cls in StripModes.__subclasses__():
                    if cls.MODE == self.strip_mode:
                        self.thread = cls(
                                self.strip, self.stop_event, self.lock)
                        self.thread.start()
                        break
            if self.strip_state == 'off':
                self.stop_event.set()
        except ValueError:
            LOG.exception('Value Error : {}'.format(self.data))
        except:
            LOG.exception('Exception : ')

    def refresh_strip(self):
        self.lock.acquire()
        self.strip.show()
        self.lock.release()
        self.refresh_timer = Timer(0.01, self.refresh_strip)
        self.refresh_timer.start()


class StripModes(Thread):

    def __init__(self, strip, stop, lock):
        super(StripModes, self).__init__()
        self.daemon = True
        self.strip = strip
        self.stop = stop
        self.lock = lock
        self.name = 'StripMode'


class Halloween(StripModes):
    MODE = 'Halloween'

    def run(self):
        LOG.debug("Running Halloween Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        crange = [colors.AQUAMARINE, colors.BROWN, colors.CYAN, colors.DARKVIOLET, colors.RED, colors.DARKGREEN, colors.DARKBLUE, colors.YELLOW, colors.BLACK]
        while not self.stop.is_set():
            i = random.randint(0, 9)
            if i != random.choice([0, 9, 1, 8, 2, 7, 3, 6, 4, 5, 6, 4, 7, 3, 8, 2, 9, 1, 0]):
                color = random.choice(crange[:-1])
                for _ in '0110010110110011010101110111':
                    self.lock.acquire()
                    if _ == random.choice(['0', '1']):
                        self.strip.set_pixel(i, color=colors.BLACK)
                    else:
                        self.strip.set_pixel(i, color=color)
                    self.lock.release()
                    time.sleep(0.05)
            else:
                self.lock.acquire()
                if self.strip.pixels[i].rgb != colors.BLACK:
                    self.strip.set_pixel(i, color=colors.BLACK)
                else:
                    self.strip.set_pixel(i, color=random.choice(crange))
                self.lock.release()
            time.sleep(random.randint(2, 5) * 0.5)
        LOG.debug("Halloween Mode Stopped")
        self.strip.all_off()

class Disco(StripModes):
    MODE = 'Disco'
    def run(self):
        LOG.debug("Starting Disco Mode")
        LOG.debug("Stip length : {}".format(self.strip.length))
        while not self.stop.is_set():
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=colors.RED)
            self.lock.release()
            time.sleep(1)
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=colors.GREEN)
            self.lock.release()
            time.sleep(1)
            self.lock.acquire()
            for i in range(self.strip.length):
                self.strip.set_pixel(i, color=colors.BLUE)
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
            color = bytearray([0,0,0])
            for i in range(255):
                color[0] = i
                self.lock.acquire()
                for p in range(self.strip.length):
                    self.strip.set_pixel(p, color=color)
                self.lock.release()
                time.sleep(0.002)
            for i in reversed(range(255)):
                color[0] = i
                self.lock.acquire()
                for p in range(self.strip.length):
                    self.strip.set_pixel(p, color=color)
                self.lock.release()
                time.sleep(0.002)
        LOG.debug("Smoothie Stopped")
        self.strip.all_off()
