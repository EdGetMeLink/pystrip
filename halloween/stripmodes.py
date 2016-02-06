from threading import Thread

class StripModes(Thread):

    def __init__(self, strip, stop, lock):
        super(StripModes, self).__init__()
        self.daemon = True
        self.strip = strip
        self.stop = stop
        self.lock = lock
        self.name = 'StripMode'
        print("stripmode init")
