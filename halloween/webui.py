from flask import Flask, make_response, request
import json
from queue import Queue
import logging
import logging.handlers
from halloween.daemon import Runner
import halloween.stripmodes as stripmodes

LOG = logging.getLogger(__name__)
SECRET_KEY = "jkdsfhkljhsfdlkjghdfkljhgkljshdfgkjshndkjlgh842u80awfiojkln"
app = Flask(__name__)

queue = Queue()
r = Runner(queue, 9)


def setup_logging():
    """
    setup logging for logger
    """
    LOG_FILE = "halloween.log"
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
    r.start()


@app.route('/', methods=['GET'])
def index():
    '''
    default route
    :return: json document containing all possible rest routes
    '''
    modes = [_.MODE for _ in stripmodes.StripModes.__subclasses__()]
    index = dict(
        title="halloween backend",
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
    queue.put(json.dumps(data))
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
    queue.put(json.dumps(data))
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
    queue.put(json.dumps(data))
    response = make_response(json.dumps(data), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == "__main__":
    setup_logging()
    app.run(host="0.0.0.0", port=8080, debug=True)
