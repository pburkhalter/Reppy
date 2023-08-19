import logging
from flask import Flask

from api.print import APIPrintEndpoints
from api.system import APISystemEndpoints


# Configure logging
logger = logging.getLogger(__name__)


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
