import os
from flask import Blueprint, request, jsonify, current_app

from lib.job import Job

class APISystemEndpoints:
    """
    Class to define API endpoints related to system operations like exit and reboot.
    """
    def __init__(self, queues, stopped_event):
        """
        Initialize the APISystemEndpoints class.

        Args:
            queues (dict): Dictionary of queues used for inter-thread communication.
        """
        self.blueprint = Blueprint('system', __name__)
        self.queues = queues
        self.stopped = stopped_event

        # Register routes
        self.blueprint.add_url_rule('/exit', 'exit', self.exit, methods=['GET'])
        self.blueprint.add_url_rule('/reboot', 'reboot', self.reboot, methods=['GET'])

    def exit(self):
        """
        Endpoint to handle system exit.

        Returns:
            tuple: JSON response and HTTP status code.
        """
        self.queues['cmd'].put(["exit", {}])
        return jsonify({"message": "Exiting..."}), 200

    def reboot(self):
        """
        Endpoint to handle system reboot.

        Returns:
            tuple: JSON response and HTTP status code.
        """
        self.queues['cmd'].put(["reboot", {}])
        return jsonify({"message": "Rebooting..."}), 200
