import logging
import logging.handlers
import sys
import time
import zmq
import json

from threading import Thread, Event
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
    def __init__(self, context, strip_length):
        super(Runner, self).__init__()
        self.daemon = True
        self.name = "Main Runner"
        self.context = context
        self.stop_event = Event()
        self.strip_mode = 'Halloween'
        self.strip_state = 'off'
        self.strip = Strip(strip_length, spi='/tmp/teststrip.spi')
        LOG.debug("Initialized Daemon")

    def run(self):

        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind('tcp://*:5558')
        exitflag = False
        while not exitflag:
            try:
                self.data = self.receiver.recv()
                LOG.debug("Data received %s" % self.data)
                self.decode()
            except (Exception, KeyboardInterrupt, SystemExit) as e:
                LOG.exception('Exception : {}'.format(e))
                exitflag = True

    def decode(self):
        try:
            self.data = json.loads(self.data.decode("utf-8"))
            self.data = self.data['strip']
            self.state = self.data.get('state', self.state)
            self.mode = self.data.get('mode', self.mode)
            if self.state == 'on':
                self.stop_event.clear()
                self.thread = self.mode(self.stop_event)
                self.thread.start()
            if self.state == 'off':
                self.stop_event.set()
        except ValueError:
            LOG.exception('Value Error : {}'.format(self.data))
        except:
            LOG.exception('Exception : ')
        

class Halloween(Thread):

    def __init__(self, strip, stop_event):
        super(Halloween, self).__init__()
        self.daemon = True
        self.stop = stop_event
        self.strip = strip

    def run(self):
        while not self.stop.is_set():
            i = random.randint(0, 9)
            if i != random.choice([0, 9, 1, 8, 2, 7, 3, 6, 4, 5, 6, 4, 7, 3, 8, 2, 9, 1, 0]):
                color = random.choice(crange[:-1])
                for _ in '0110010110110011010101110111':
                    if _ == random.choice(['0', '1']):
                        self.strip.set_pixel(i, color=colors.BLACK)
                    else:
                        self.strip.set_pixel(i, color=color)
                    self.strip.show()
                    time.sleep(0.05)
            else:
                if self.strip.pixels[i].rgb != colors.BLACK:
                    self.strip.set_pixel(i, color=colors.BLACK)
                else:
                    self.strip.set_pixel(i, color=random.choice(crange))
                self.strip.show()
            time.sleep(random.randint(2, 5) * 0.5)
        self.strip.all_off()
