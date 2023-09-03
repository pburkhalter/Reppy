import os
import yaml
import json
import logging
import datetime
from cerberus import Validator

# Configure logging
logger = logging.getLogger(__name__)

# Paths and filenames
SYSTEM_PATH = "src/config/system.json"
SETTINGS_PATH = "src/config/settings.yaml"
VALIDATION_SCHEMA = "src/config/validate.yaml"

# Default system settings
SYSTEM_DEFAULTS = {
    "is_calibrated": False,
    "calibration_time": False,
    "motor_position": False,
    "initial_setup_time": datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
    "last_job_id": None
}


def parse_yaml(filepath):
    """
    Parse and load YAML content from a file.

    Args:
        filepath (str): The path to the YAML file.

    Returns:
        dict: Parsed YAML content as a dictionary.
    """
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
    """
    Singleton class to manage application settings.
    """
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
        """
        Retrieve a setting by its key.

        Args:
            key (str): The key to look up.

        Returns:
            The value associated with the key.
        """
        if key in self.settings:
            return self.settings[key]
        else:
            raise KeyError(f"'{key}' not found")

    def load(self, filepath):
        """
        Load settings from a YAML file.

        Args:
            filepath (str): The path to the YAML file.
        """
        self.filepath = filepath
        self.settings = parse_yaml(filepath)

    def validate(self, schema):
        """
        Validate loaded settings against a validation schema.

        Args:
            schema (str): The path to the validation schema.

        Returns:
            bool: True if validation is successful, otherwise raises an error.
        """
        self.schema = parse_yaml(schema)
        validator = Validator(self.schema)

        if validator.validate(self.settings):
            return True
        else:
            logger.error(f"Validation errors: {validator.errors}")
            raise KeyError("Settings do contain validation errors!")


class SystemSettings:
    """
    Singleton class to manage system settings.
    """
    _instance = None

    def __init__(self):
        self.filepath = None
        self.settings = {}

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __del__(self):
        self.save()

    def __getitem__(self, key):
        """
        Retrieve a system setting by its key.

        Args:
            key (str): The key to look up.

        Returns:
            The value associated with the key.
        """
        if key in self.settings:
            return self.settings[key]
        else:
            raise KeyError(f"'{key}' not found")

    def __setitem__(self, key, value):
        """
        Set a system setting by its key and save it.

        Args:
            key (str): The key to set.
            value: The value to set.
        """
        if key in self.settings:
            self.settings[key] = value
            self.save()
        else:
            raise KeyError(f"'{key}' not found")

    def load(self, filepath):
        """
        Load system settings from a JSON file.

        Args:
            filepath (str): The path to the JSON file.
        """
        self.filepath = filepath
        try:
            with open(self.filepath, 'r') as f:
                self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = SYSTEM_DEFAULTS.copy()
            self.save()

    def save(self):
        """
        Save system settings to a JSON file.
        """
        directory, filename = os.path.split(self.filepath)
        os.makedirs(directory, exist_ok=True)
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except PermissionError as e:
            logger.error(f"A permission error occurred while saving the system settings file. Reason: {e}")
        except OSError as e:
            logger.error(f"An error occurred while saving the system settings file. Reason: {e}")


# Create instances of system settings and settings
system_dict = SystemSettings()
system_dict.load(SYSTEM_PATH)

settings_dict = Settings()
settings_dict.load(SETTINGS_PATH)
settings_dict.validate(VALIDATION_SCHEMA)
