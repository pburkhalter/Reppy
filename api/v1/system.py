from flask import Blueprint, jsonify, current_app
import os


system = Blueprint('system', __name__)


@system.route('/reboot', methods=['POST'])
def reboot():
    # Logic to reboot the system. This can be dangerous and should be properly authenticated/authorized.
    os.system('sudo reboot')
    return jsonify({"message": "System rebooting..."})
