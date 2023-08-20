import logging
import os

from flask import Flask

from api.print import APIPrintEndpoints
from api.system import APISystemEndpoints
from settings import settings_dict

# Configure logging
logger = logging.getLogger(__name__)

# Set up werkzeug (flask) logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

file_handler = logging.FileHandler(os.path.join(settings_dict['system']['paths']['logging'], "flask.log"))
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)


class APIController:

    def __init__(self, queues, stop_event):
        self.queues = queues
        self.stopped = stop_event

        self.blueprints = {
            'print': APIPrintEndpoints,
            'system': APISystemEndpoints
        }

        self.app = Flask(__name__)
        self.register_blueprints()
        self.run()

    def register_blueprints(self):
        for blueprint in self.blueprints:
            blueprint_instance = self.blueprints[blueprint](self.queues)
            self.app.register_blueprint(blueprint_instance.blueprint)

    def run(self, debug=False):
        self.app.run(debug=debug)
