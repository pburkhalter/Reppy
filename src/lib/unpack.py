import datetime
import json
import os
import re
import zipfile
import uuid
import logging
import configparser

from settings import settings_dict


# Configure logging
logger = logging.getLogger(__name__)


"""
sample-print.zip (sliced with Chitubox)
│
├── run.gcode
│
├── 1.png
├── 2.png
├── 3.png
│
│   ... (more png files for each slice/layer) ...
│
├── 1000.png
"""


class UnpackerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Unpacker:
    def __init__(self, zip_file_path=None):
        self.zip_file = zip_file_path
        self.directory_root = settings_dict['system']['paths']['unpack']
        self.directory = None

        self.extracted_at = datetime.datetime.now()
        self.images = {}
        self.config = {}

    def unpack(self, zip_file=None):
        if zip_file:
            self.zip_file = zip_file
        elif not getattr(self, 'zip_file', None):
            raise UnpackerError("ZIP-File is not set!")

        logger.debug(f"Unpacking zip file '{self.zip_file}'")
        if self.unpack_zip():
            if not self.parse_images():
                raise UnpackerError("Could not parse images")
            if not self.parse_gcode():
                raise UnpackerError("Could not parse GCODE file")

    def unpack_zip(self):
        try:
            subdirectory_date = self.extracted_at.strftime("%Y%m%d%H%M%S")
            subdirectory_uuid = uuid.uuid4().hex
            subdirectory_name = subdirectory_date + "-" + subdirectory_uuid

            self.directory = os.path.join(self.directory_root, subdirectory_name)
            os.makedirs(self.directory, exist_ok=True)

            with zipfile.ZipFile(self.zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.directory)

            logger.info(f"Successfully unpacked zip '{self.zip_file}' to '{self.directory}'.")
            return self.directory
        except Exception as e:
            logger.error(f"Error while unpacking: {e}")
            return None

    def parse_images(self):
        try:
            # Get a list of PNG files in the specified path
            png_files = [f for f in os.listdir(self.directory) if f.lower().endswith('.png')]

            # Extract numbers from the filenames and sort them
            numbered_files = []
            for file in png_files:
                match = re.search(r'(\d+)', file)
                if match:  # Check if a number exists in the filename
                    num = int(match.group(1))
                    numbered_files.append((num, file))

            numbered_files.sort()

            # Check if the files are numbered consecutively
            numbers = [num for num, _ in numbered_files]
            if any(a - b != 1 for a, b in zip(numbers[1:], numbers[:-1])):
                logger.error("Files not numbered consecutively!")
                self.images = {}
            else:
                # Create dict
                self.images = {num: {'filepath': os.path.join(self.directory, file)} for num, file in numbered_files}
            return self.images

        except OSError as e:
            logger.error(f"Error while listing files in directory: {e}")
            return {}

    def parse_gcode(self):
        config_file = os.path.join(self.directory, "run.gcode")
        config = configparser.ConfigParser()

        # Check if file exists
        try:
            with open(config_file, 'r') as f:
                pass
        except FileNotFoundError:
            logger.error(f"File '{config_file}' not found.")
            return {}

        # TODO: For now we dont need the gcode

        return {'content': None}
