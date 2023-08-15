import datetime
import json
import os
import re
import zipfile
import uuid
import logging
import configparser

from settings import settings_dict


"""
sample-print.zip
│
├── config.txt
│
├── 00001.png
├── 00002.png
├── 00003.png
│
│   ... (more png files for each slice/layer) ...
│
├── 01000.png
"""


class UnpackerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Unpacker:
    def __init__(self, zip_file_path=None):
        self.zip_file = zip_file_path
        self.directory_root = settings_dict['system']['path']['unpack']
        self.directory = None

        self.extracted_at = datetime.datetime.now()
        self.images = {}
        self.config = {}

    def unpack(self, zip_file=None):
        if zip_file:
            self.zip_file = zip_file
        elif not getattr(self, 'zip_file', None):
            raise UnpackerError("ZIP-File is not set!")

        if self.unpack_zip():
            if not self.parse_images():
                raise UnpackerError("Could not parse images")
            if not self.parse_config():
                raise UnpackerError("Could not parse config")

    def unpack_zip(self):
        try:
            subdirectory_date = self.extracted_at.strftime("%Y%m%d%H%M%S")
            subdirectory_uuid = uuid.uuid4().hex
            subdirectory_name = subdirectory_date + "-" + subdirectory_uuid

            self.directory = os.path.join(self.directory_root, subdirectory_name)
            os.makedirs(self.directory, exist_ok=True)

            with zipfile.ZipFile(self.zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.directory)

            logging.info(f"Successfully unpacked zip '{self.zip_file}' to '{self.directory}'.")
            return self.directory
        except Exception as e:
            logging.error(f"Error while unpacking: {e}")
            return None

    def parse_images(self):
        try:
            # Get a list of PNG files in the specified path and sort them
            png_files = sorted([f for f in os.listdir(self.directory) if f.lower().endswith('.png')])

            # Extract numbers from the filenames
            numbers = [int(re.search(r'(\d+)', file).group(1)) for file in png_files if re.search(r'(\d+)', file)]

            # Check if the files are numbered consecutively
            if any(a - b != 1 for a, b in zip(numbers[1:], numbers[:-1])):
                logging.error("Files not numbered consecutively!")
                self.images = {}
            else:
                # create dict
                self.images = {num: {'filepath': f"{num}.png"} for num in numbers}

            return self.images

        except OSError as e:
            logging.error(f"Error while listing files in directory: {e}")
            return {}

    def parse_config(self):
        config_file = os.path.join(self.directory, "config.txt")
        config = configparser.ConfigParser()

        # Check if file exists
        try:
            with open(config_file, 'r') as f:
                pass
        except FileNotFoundError:
            logging.error(f"File '{config_file}' not found.")
            return {}

        # Try reading and parsing the (INI-like) config-file
        try:
            config.read(config_file)
        except configparser.Error as e:
            logging.error(f"Could not parse the config-file: {e}")
            return {}

        # Convert to a dictionary
        return {section: dict(config[section]) for section in config.sections()}
