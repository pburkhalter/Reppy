import os
from uuid import uuid4

from flask import Blueprint, request, jsonify, current_app

from settings import settings_dict
from lib.job import PrintJob


UPLOAD_FOLDER = settings_dict['system']['paths']['upload']
ALLOWED_EXTENSIONS = settings_dict['system']['filetypes']['allowed']


def allowed_file(filename):
    """Check if the file has the allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class APIPrintEndpoints:
    def __init__(self, queues):
        self.blueprint = Blueprint('print', __name__)
        self.queues = queues

        # Register routes
        self.blueprint.add_url_rule('/start', 'start', self.start, methods=['POST'])
        self.blueprint.add_url_rule('/stop', 'stop', self.stop, methods=['POST'])
        self.blueprint.add_url_rule('/level', 'calibrate', self.level, methods=['POST'])
        self.blueprint.add_url_rule('/upload', 'upload', self.upload, methods=['POST'])

    def start(self):
        # Logic to start printing
        job = PrintJob("printer", "PRINT", )
        sj = job.serialize()
        self.queues['print'].put(sj)
        return jsonify({"message": "Print started"}), 200

    def stop(self):
        # Logic to stop printing
        return jsonify({"message": "Print stopped"}), 200

    def level(self):
        # Logic to level the z-axis
        return jsonify({"message": "Starting leveling"}), 200

    def upload(self):
        # Check if the post request has the file part and it's not empty
        if 'file' not in request.files or request.files['file'].filename == '':
            return jsonify({"error": "No file part"}), 400

        # Check if the file-type (extension) is allowed
        if not allowed_file(request.files['file'].filename):
            return jsonify({"error": "File type not allowed"}), 400

        file = request.files['file']
        filename = uuid4().hex
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        tm = PrintJob("printer", "PRINT")
        tm.data = {'filepath': filepath}
        self.queues['print'].put(tm.serialize())

        return jsonify({"message": "File uploaded successfully", "path": filepath}), 200
