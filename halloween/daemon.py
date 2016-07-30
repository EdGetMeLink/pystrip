import logging
import logging.handlers
import random
from halloween.colors import Color
import sys
import time
import json
import math
from queue import Empty
import random

from threading import Thread, Event, Timer, Lock
from halloween.strip import ArduinoStrip
import halloween.stripmodes as stripmodes


LOG = logging.getLogger(__name__)

colors = Color()

def setup_logging():
    LOG_FILE = "halloween.log"
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    formatter = (
        '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(LOG_FILE,
            maxBytes=1024*1024,
            backupCount=5)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


class Runner(Thread):

    def __init__(self, queue, strip_length):
        super(Runner, self).__init__()
        self.daemon = True
        self.name = "Main Runner"
        self.queue = queue
        self.stop_event = Event()
        self.strip_mode = 'Mover'
        self.strip_state = 'on'
        self.thread = None
        self.lock = Lock()
        #self.strip = Strip(strip_length)
        self.strip = ArduinoStrip(
                x=3, 
                y=3,
                host="http://10.10.20.12/strip")
        LOG.debug("Initialized Daemon")

    def run(self):

        exitflag = False
        LOG.debug("Starting Timer")
        while not exitflag:
            try:
                self.data = self.queue.get()
                LOG.debug("Data received %s" % self.data)
                self.decode()
            except (Exception, KeyboardInterrupt, SystemExit) as e:
                LOG.exception('Exception : {}'.format(e))
                exitflag = True

    def decode(self):
        try:
            self.data = json.loads(self.data)
            self.data = self.data['strip']
            self.strip_state = self.data.get('state', self.strip_state)
            self.strip_mode = self.data.get('mode', self.strip_mode)
            self.strip.brightness = int(self.data.get('brightness', self.strip.brightness))
            if self.data.get('mode', None):
                self.strip.all_off()
            if self.strip_state == 'on':
                self.stop_event.set()
                if self.thread:
                    LOG.debug("Waiting for old thread to stop")
                    self.thread.join()
                    LOG.debug("Thread stopped")
                self.stop_event.clear()
                for cls in stripmodes.StripModes.__subclasses__():
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
