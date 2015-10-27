from flask import Flask, make_response, request
import json
from Queue import Queue
import logging
import logging.handlers
from halloween.daemon import Runner

LOG = logging.getLogger(__name__)
SECRET_KEY = "jkdsfhkljhsfdlkjghdfkljhgkljshdfgkjshndkjlgh842u80awfiojkln"
app = Flask(__name__)

queue = Queue()
r = Runner(queue, 10)

def setup_logging():
    LOG_FILE = "halloween.log"
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s\n\t%(threadName)s - %(levelname)s - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(LOG_FILE,
            maxBytes=1024*1024,
            backupCount=5)
    file_handler.setLevel(logging.DEBUG)
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
    index = dict(
            title="halloween backend",
            description="RESTful Halloween PI backend",
            version="0.0.1",
            _links={
                'strip':{
                    'href': '/strip',
                    'description': 'get information about curent strip config',
                    'templated': False
                    },
                'stripmode':{
                    'href': '/strip/mode',
                    'description': 'posible values: halloween, disco',
                    'templated': False
                    },
                'stripstate':{
                    'href': '/strip/state',
                    'description': 'set strip state on or off',
                    'templated': False
                    },
                }
            )
    response = make_response(json.dumps(index), 200)
    response.headers['Content-Type'] = 'application/hal+json'
    return response

@app.route('/strip/state/<state>', methods=['POST', 'GET'])
def stripstate(state):
    data = {
        'strip': {
            'state': state
        }
    }
    queue.put(json.dumps(data))
    response = make_response(json.dumps(data), 200)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/strip/mode/<mode>', methods=['POST', 'GET'])
def stripmode(mode):
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
    app.run(host='0.0.0.0', port=8080, debug=True)
