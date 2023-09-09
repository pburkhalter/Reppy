import logging
import RPi.GPIO as GPIO
from settings import settings_dict
from utils.raspi import is_raspberrypi

# Configure logging
logger = logging.getLogger(__name__)

"""
This module provides a convenient way to manage GPIO configurations on a Raspberry Pi.
It uses the RPi.GPIO library for GPIO operations and a custom settings_dict for pin mappings.
"""

# Raspberry Pi GPIO Pin Layout
# (ASCII diagram here)

# GPIO modes and levels mapping
GPIO_MODES = {
    "OUT": GPIO.OUT,
    "IN": GPIO.IN
}

GPIO_LEVELS = {
    "UP": GPIO.PUD_UP,
    "DOWN": GPIO.PUD_DOWN
}


class GPIOConfigError(Exception):
    """
    Custom exception for GPIO configuration errors.
    """

    def __init__(self, message):
        super().__init__(message)


class GPIOConfig:
    """
    Singleton class to manage GPIO configurations on a Raspberry Pi.
    """
    # Singleton
    _instance = None

    pins = {}
    board_revision = None

    def __init__(self):
        """
        Initialize the GPIOConfig instance.
        """
        # set pin-layout to BCM
        GPIO.setmode(GPIO.BCM)

        if not is_raspberrypi():
            logger.info("Not running on a raspberry Pi. Setting board revision to '3' for local development...")
            self.board_revision = 3  # for local dev with fake pi
        else:
            # get the board revision
            self.board_revision = GPIO.RPI_REVISION

    def __new__(cls, **kwargs):
        """
        Create a new instance or return the existing instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getitem__(self, key):
        """
        Retrieve the GPIO pin number for a given key.

        Parameters:
            key (str): The key for the GPIO pin.

        Returns:
            int: The GPIO pin number.

        Raises:
            KeyError: If the key is not found.
        """
        if key in self.pins:
            return self.pins[key]
        else:
            raise KeyError(f"'{key}' not found")

    def set_pin(self, pin, mode, level=None):
        """
        Set the GPIO pin with the given mode and level.

        Parameters:
            pin (int): The GPIO pin number.
            mode (str): The GPIO mode ('IN' or 'OUT').
            level (str, optional): The GPIO level ('UP' or 'DOWN').

        Raises:
            GPIOConfigError: If the mode or level is invalid.
        """
        if mode not in GPIO_MODES:
            raise GPIOConfigError(f"GPIO Mode not found: {mode}")

        if mode == 'IN' and level not in GPIO_LEVELS:
            raise GPIOConfigError(f"GPIO Level not found: {level}")

        gpio_mode = GPIO_MODES.get(mode)
        gpio_level = {'pull_up_down': GPIO_LEVELS.get(level)} if GPIO_LEVELS.get(level) else {}

        try:
            GPIO.setup(pin, gpio_mode, **gpio_level)
        except Exception as e:
            raise GPIOConfigError(f"Error while setting GPIO Pin. Reason: {e}")

    def setup(self, pins):
        """
        Set up multiple GPIO pins based on the given dictionary.

        Parameters:
            pins (dict): A dictionary containing pin configurations.
        """
        for name in pins:
            logger.info(f"Configuring Pin {pins[name].get('pin')} for {name}")
            self.set_pin(
                pins[name].get('pin'),
                pins[name].get('mode'),
                pins[name].get('level', None)
            )
            self.pins[name] = pins[name].get('pin')

    def cleanup(self):
        """
        Clean up the GPIO settings.
        """
        GPIO.cleanup()


# Create an instance of GPIOConfig and set up GPIO pins based on settings
gpio_dict = GPIOConfig()
gpio_dict.setup(settings_dict['gpio'])
