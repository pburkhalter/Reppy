import os
from flask import Blueprint, request, jsonify, current_app

from lib.task import TaskMessage


class APISystemEndpoints:
    def __init__(self, queues):
        self.blueprint = Blueprint('system', __name__)
        self.queues = queues

        # Register routes
        self.blueprint.add_url_rule('/exit', 'exit', self.exit, methods=['POST'])
        self.blueprint.add_url_rule('/reboot', 'reboot', self.reboot, methods=['POST'])

    def exit(self):
        # Logic to start printing
        task = TaskMessage("printer", "PRINT", )
        st = task.serialize()
        self.queues['print'].put(st)
        pass

    def reboot(self):
        # Logic to reboot
        pass
