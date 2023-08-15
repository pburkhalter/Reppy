from flask import Blueprint, request, jsonify, current_app

from lib.task import TaskMessage

printer = Blueprint('printer', __name__)


@printer.route('/start', methods=['POST'])
def start_print():
    # Logic to start printing
    task = TaskMessage()
    st = task.serialize()
    current_app.q.put(st)
    pass


@printer.route('/stop', methods=['POST'])
def stop_print():
    # Logic to stop printing
    pass


@printer.route('/level', methods=['POST'])
def level_z_axis():
    # Logic to level the Z axis
    pass



