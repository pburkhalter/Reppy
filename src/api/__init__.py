import logging
import os
from flask import Flask
from api.print import APIPrintEndpoints
from api.system import APISystemEndpoints
from settings import settings_dict

# Setup logging for this module
logger = logging.getLogger(__name__)

# Setup logging for Flask (werkzeug)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
file_handler = logging.FileHandler(os.path.join(settings_dict['system']['paths']['logging'], "flask.log"))
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)


class APIController:
    """
    Class to initialize and control the Flask API.
    """

    def __init__(self, queues, stop_event):
        """
        Initialize the APIController class.

        Args:
            queues (dict): Dictionary of queues used for inter-thread communication.
            stop_event (threading.Event): Event to signal the thread to stop.
        """
        self.queues = queues
        self.stopped = stop_event

        # Blueprints mapping
        self.blueprints = {
            'print': APIPrintEndpoints,
            'system': APISystemEndpoints
        }

        # Initialize Flask app
        self.app = Flask(__name__)

        # Register blueprints
        self.register_blueprints()

        # Run the app
        self.run()

    def register_blueprints(self):
        """
        Register all the blueprints to the Flask app.
        """
        for blueprint in self.blueprints:
            blueprint_instance = self.blueprints[blueprint](self.queues, self.stopped)
            self.app.register_blueprint(blueprint_instance.blueprint)

    def run(self, debug=False):
        """
        Run the Flask application.

        Args:
            debug (bool, optional): Whether to run the app in debug mode. Defaults to False.
        """
        self.app.run(debug=debug, port=8080)
