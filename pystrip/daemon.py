import logging
import logging.handlers
from pystrip.colors import Color
import json


from threading import Thread, Event, Lock
from pystrip.strip import ArduinoStrip, NoStrip, Strip
import pystrip.stripmodes as stripmodes


LOG = logging.getLogger(__name__)

colors = Color()


class Runner(Thread):

    def __init__(self, queue, strip_length, striptype=None):
        super(Runner, self).__init__()
        self.daemon = True
        self.name = "Main Runner"
        self.queue = queue
        self.stop_event = Event()
        self.strip_mode = 'off'
        self.strip_state = 'on'
        self.thread = None
        self.lock = Lock()
        if striptype == 'Strip':
            self.strip = Strip(strip_length)
        elif striptype == 'Arduino':
            self.strip = ArduinoStrip(
                x=3, y=3, host="http://10.10.20.12/strip")
        else:
            self.strip = NoStrip(strip_length)
        LOG.debug("Initialized Daemon")

    def run(self):

        exitflag = False
        LOG.debug("Starting Timer")
        while not exitflag:
            try:
                self.data = self.queue.get()
                LOG.debug("Data received %s" % self.data)
                self.decode()
                self.execute()
            except (Exception, KeyboardInterrupt, SystemExit) as e:
                LOG.exception('Exception : {}'.format(e))
                exitflag = True

    def decode(self):
        """
        decode incoming json and map received data
        """
        try:
            self.data = json.loads(self.data)
            self.params = json.loads(self.data.get('params', None))
            self.data = self.data['strip']
            self.strip_state = self.data.get('state', self.strip_state)
            self.strip_mode = self.data.get('mode', self.strip_mode)
            self.strip.brightness = int(
                self.data.get('brightness', self.strip.brightness))
            self.color_decode(self.data.get('color'))
        except ValueError:
            LOG.exception('Value Error : {}'.format(self.data))
        except:
            LOG.exception('Exception : ')

    def _stop_thread(self):
        if self.thread and self.thread.is_alive():
            LOG.debug("Waiting for thread to stop (none mode)")
            self.thread.join()
            LOG.debug("Thread stopped")
        self.stop_event.clear()


    def execute(self):
        """
        execute thread according to strip mode and state
        """
        if self.strip_mode == "off":
            LOG.debug("strip_mode off")
            self.strip.all_off()
            self.stop_event.set()
            self._stop_thread()

        if self.strip_state == 'on':
            self.stop_event.set()
            self._stop_thread()
            for cls in stripmodes.StripModes.__subclasses__():
                if cls.MODE == self.strip_mode:
                    self.thread = cls(
                        self.strip,
                        self.stop_event,
                        self.lock,
                        self.params)
                    self.thread.start()
                    break

    def color_decode(self, colordata):
        """
        decode and set strip color to colordata
        """
        if not colordata:
            return
        colors = []
        for color in colordata:
            colors.append(int(color, 10))
        for i in range(self.strip.length):
            self.strip.set_pixel(i, color=bytearray(colors))
        self.strip.show()
        return
