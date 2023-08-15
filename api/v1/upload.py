import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from settings import settings_dict


upload = Blueprint('upload', __name__)


UPLOAD_FOLDER = settings_dict['system']['paths']['upload']
ALLOWED_EXTENSIONS = {'zip'}


def allowed_file(filename):
    """Check if the file has the allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # If user does not select file, browser submits an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # This ensures the filename is safe to use
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully", "path": filepath}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400


