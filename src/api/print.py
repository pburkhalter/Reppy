import os
from uuid import uuid4
from flask import Blueprint, request, jsonify, current_app
from settings import settings_dict
from lib.job import Job

UPLOAD_FOLDER = settings_dict['system']['paths']['upload']
ALLOWED_EXTENSIONS = settings_dict['system']['filetypes']['allowed']

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class APIPrintEndpoints:
    """
    Class to define API endpoints related to print operations like start, stop, level, and upload.
    """
    def __init__(self, queues, stopped_event):
        """
        Initialize the APIPrintEndpoints class.

        Args:
            queues (dict): Dictionary of queues used for inter-thread communication.
        """
        self.blueprint = Blueprint('print', __name__)
        self.queues = queues
        self.stopped = stopped_event

        # Register routes
        self.blueprint.add_url_rule('/start', 'start', self.start, methods=['GET'])
        self.blueprint.add_url_rule('/stop', 'stop', self.stop, methods=['GET'])
        self.blueprint.add_url_rule('/level', 'calibrate', self.level, methods=['GET'])
        self.blueprint.add_url_rule('/upload', 'upload', self.upload, methods=['POST'])

    def start(self):
        """
        Endpoint to start the printing process.

        Returns:
            tuple: JSON response and HTTP status code.
        """
        self.queues['cmd'].put(["start", {}])
        return jsonify({"message": "Print started"}), 200

    def stop(self):
        """
        Endpoint to stop the printing process.

        Returns:
            tuple: JSON response and HTTP status code.
        """
        self.queues['cmd'].put(["stop", {}])
        return jsonify({"message": "Print stopped"}), 200

    def level(self):
        """
        Endpoint to initiate the leveling of the z-axis.

        Returns:
            tuple: JSON response and HTTP status code.
        """
        # Logic to level the z-axis can be added here
        self.queues['cmd'].put(["level", {}])
        return jsonify({"message": "Starting leveling"}), 200

    def upload(self):
        """
        Endpoint to handle file upload for printing.

        Returns:
            tuple: JSON response and HTTP status code.
        """
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

        tm = Job(filepath)
        self.queues['print'].put(tm.serialize())
        self.queues['cmd'].put(["start", {}])

        return jsonify({"message": "File uploaded successfully", "path": filepath}), 200
