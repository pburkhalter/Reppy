import os
from flask import Blueprint, request, jsonify, current_app

from lib.job import PrintJob


class APISystemEndpoints:
    def __init__(self, queues):
        self.blueprint = Blueprint('system', __name__)
        self.queues = queues

        # Register routes
        self.blueprint.add_url_rule('/exit', 'exit', self.exit, methods=['POST'])
        self.blueprint.add_url_rule('/reboot', 'reboot', self.reboot, methods=['POST'])

    def exit(self):
        # Logic to exiting
        return jsonify({"message": "Exiting..."}), 200

    def reboot(self):
        # Logic to rebooting
        return jsonify({"message": "Rebooting..."}), 200
