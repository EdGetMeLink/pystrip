import logging
import logging.handlers
import sys
import time
import zmq

from threading import Thread

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
    def __init__(self, context):
        super(Runner, self).__init__()
        self.daemon = True
        self.name = "Main Runner"
        self.context = context
        LOG.debug("Initialized Daemon")

    def run(self):

        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind('tcp://*:5558')
        exitflag = False
        while not exitflag:
            try:
                self.data = self.receiver.recv()
                LOG.debug("Data received %s" % self.data)
                time.sleep(2)
            except (Exception, KeyboardInterrupt, SystemExit) as e:
                LOG.exception('Exception : {}'.format(e))
                exitflag = True
