from flask import Flask, make_response, request
import json
import zmq
import logging
import logging.handlers
from halloween.daemon import Runner

LOG = logging.getLogger(__name__)
SECRET_KEY = "jkdsfhkljhsfdlkjghdfkljhgkljshdfgkjshndkjlgh842u80awfiojkln"
app = Flask(__name__)
context = zmq.Context()
# Socket with direct access to the sink: used to syncronize start of batch
sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")


def setup_logging():
    LOG_FILE = "halloween.log"
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    formatter = '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s'
    file_handler = logging.handlers.RotatingFileHandler(LOG_FILE,
            maxBytes=1024*1024,
            backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    #file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    #console_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


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
                    }
                }
            )
    response = make_response(json.dumps(index), 200)
    response.headers['Content-Type'] = 'application/hal+json'
    return response

@app.route('/strip/state/<state>', methods=['GET'])
def strip_state(state):
    sink.send_string(state)
    resp = dict(
            strip_state=state
            )
    response = make_response(json.dumps(resp), 200)
    response.headers['Content-Type'] = 'application/json'
    return response



if __name__ == "__main__":
    setup_logging()
    r = Runner(context)
    r.daemon = True
    print("Starting Daemon")
    r.start()
    app.run(host='0.0.0.0', port=8080, debug=True)
