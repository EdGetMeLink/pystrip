from flask import Flask, make_response, request
import json
import logging

LOG = logging.getLogger(__name__)
SECRET_KEY = "jkdsfhkljhsfdlkjghdfkljhgkljshdfgkjshndkjlgh842u80awfiojkln"


def setup_logging():
    LOG_FILE = "/var/log/halloween.log"
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    formatter =
        '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s'0
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


def create_app():
    app = Flask(__name__)
    return app

@app.route('/', methods=['GET'])
def index():
    index = dict(
            title="halloween backend",
            description="RESTful Halloween PI backend",
            version="0.0.1",
            _links={
                'strip':{
                    'href': '/strip',
                    'description': 'get information about curent strip config'
                    'templated': False
                    }
                }
            )
    response = make_response(json.dumps(index), 200)
    response.headers['Content-Type'] = 'application/hal+json'
    return response



if __name__ == "__main__":
    setup_logging()
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
