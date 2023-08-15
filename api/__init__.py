import queue
from flask import Flask


app = Flask(__name__)
q = queue.Queue()


def create_app():
    from api.v1 import blueprint as api_v1_blueprint

    app.register_blueprint(api_v1_blueprint, url_prefix='/api/v1')

    return app