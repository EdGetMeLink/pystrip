from flask import Flask, make_response
import json
from queue import Queue
import logging
import logging.handlers
from pystrip.config import load_config
from pystrip.daemon import Runner
import pystrip.stripmodes as stripmodes

LOG = logging.getLogger(__name__)
SECRET_KEY = "jkdsfhkljhsfdlkjghdfkljhgkljshdfgkjshndkjlgh842u80awfiojkln"
app = Flask(__name__)


def setup_logging():
    """
    setup logging for logger
    """
    LOG_FILE = "pystrip.log"
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s\n\t%(threadName)s - %(levelname)s - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(LOG_FILE,
                                                        maxBytes=1024 * 1024,
                                                        backupCount=5)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


@app.before_first_request
def daemon_starter():
    print("Starting Daemon")
    app.runner.start()


@app.route('/', methods=['GET'])
def index():
    '''
    default route
    :return: json document containing all possible rest routes
    '''
    modes = [_.MODE for _ in stripmodes.StripModes.__subclasses__()]
    index = dict(
        title="pystrip backend",
        description="RESTful Halloween PI backend",
        version="0.0.1",
        _links={
            'strip': {
                'href': '/strip',
                'description': 'get information about curent strip config',
                'templated': False
            },
            'strip mode': {
                'href': '/strip/mode',
                'description': 'posible values: {}'.format(', '.join(modes)),
                'templated': False
            },
            'strip state': {
                'href': '/strip/state',
                'description': 'set strip state on or off',
                'templated': False
            },
            'strip brightness': {
                'href': '/strip/brightness',
                'description': 'set strip brightness in percent',
                'templated': False
            },
            'strip color': {
                'href': '/strip/color/<red>/<green>/<blue>',
                'description': 'set strip uniform color (rgb)',
                'templated': False
            },
        }
    )
    response = make_response(json.dumps(index), 200)
    response.headers['Content-Type'] = 'application/hal+json'
    return response


@app.route('/strip/state/<state>', methods=['POST', 'GET'])
def stripstate(state):
    """
    set strip state to on or off
    :type state: string
    """
    data = {
        'strip': {
            'state': state
        }
    }
    app.queue.put(json.dumps(data))
    response = make_response(json.dumps(data), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/strip/brightness/<value>', methods=['POST', 'GET'])
def stripbright(value):
    data = {
        'strip': {
            'brightness': value
        }
    }
    app.queue.put(json.dumps(data))
    response = make_response(json.dumps(data), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/strip/mode/<mode>', methods=['POST', 'GET'])
def stripmode(mode):
    """
    set the stripmode
    :type mode: ony valid strip mode  (class) defined in daemon
    """
    data = {
        'strip': {
            'mode': mode
        }
    }
    app.queue.put(json.dumps(data))
    response = make_response(json.dumps(data), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/strip/color/<path:colordata>', methods=['POST', 'GET'])
def stripcolor(colordata):
    """
    set the strip uniform color
    """
    colors = colordata.split("/")
    data = {
        'strip': {
            'color': colors
        }
    }
    for color in colors:
        try:
            int(color, 10)
        except ValueError:
            response = make_response(json.dumps(data), 400)
            response.headers['Content-Type'] = 'application/json'
            return response
    app.queue.put(json.dumps(data))
    response = make_response(json.dumps(data), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == "__main__":
    setup_logging()
    cfg = load_config()
    striptype = cfg.get("general", "striptype")
    striplenght = int(cfg.get("general", "striplenght"))
    app.queue = Queue()
    app.runner = Runner(app.queue, striplenght, striptype)

    app.run(host="0.0.0.0", port=8081, debug=True)
