import yaml
import json
import logging
import datetime
from cerberus import Validator


# Configure logging
logger = logging.getLogger(__name__)


SYSTEM_PATH = "src/config/system.json"
SETTINGS_PATH = "src/config/settings.yaml"
VALIDATION_SCHEMA = "src/config/validate.yaml"

SYSTEM_DEFAULTS = {
    "is_calibrated": False,
    "calibration_time": False,
    "motor_position": False,
    "initial_setup_time": datetime.time(),
    "last_task_id": None
}


def parse_yaml(filepath):
    try:
        with open(filepath, "r") as yaml_file:
            yaml_content = yaml_file.read()
            parsed_dict = yaml.safe_load(yaml_content)
            return parsed_dict
    except FileNotFoundError:
        logger.error(f"The file '{filepath}' was not found.")
        raise
    except PermissionError:
        logger.error(f"Insufficient permissions to read the file '{filepath}'.")
        raise
    except yaml.YAMLError as exc:
        logger.error(f"An error occurred while parsing the YAML content. {exc}")
        raise


class Settings:
    # Singleton
    _instance = None

    def __init__(self):
        self.filepath = None
        self.settings = {}
        self.schema = {}

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getitem__(self, key):
        if key in self.settings:
            return self.settings[key]
        else:
            raise KeyError(f"'{key}' not found")

    def load(self, filepath):
        self.filepath = filepath
        self.settings = parse_yaml(filepath)

    def validate(self, schema):
        self.schema = parse_yaml(schema)
        validator = Validator(self.schema)

        if validator.validate(self.settings):
            return True
        else:
            logger.error(f"Validation errors: {validator.errors}")
            raise KeyError("Settings do contain validation errors!")


class SystemSettings:
    # Singleton
    _instance = None

    def __init__(self):
        self.filepath = None
        self.settings = {}

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getitem__(self, key):
        if key in self.settings:
            return self.settings[key]
        else:
            raise KeyError(f"'{key}' not found")

    def __setitem__(self, key, value):
        if key in self.settings:
            self.settings[key] = value
        else:
            raise KeyError(f"'{key}' not found")

    def load(self, filepath):
        self.filepath = filepath
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file is not found or has invalid JSON, return a copy of the default settings
            self.settings = SYSTEM_DEFAULTS.copy()

            # We assume this is the first time running reppy, so we set the initial setup time
            self.settings['initial_setup_time'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            self.save()
            return self.settings

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.settings, f, indent=4)


system_dict = SystemSettings()
system_dict.load(SYSTEM_PATH)

settings_dict = Settings()
settings_dict.load(SETTINGS_PATH)
settings_dict.validate(VALIDATION_SCHEMA)
