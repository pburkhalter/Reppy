import io
import sys

# Importing Raspberry Pi utility functions
from utils.raspi import is_raspberrypi, load_fake_rpi

"""
This script checks if the current environment is a Raspberry Pi.
If it is not, it loads a fake Raspberry Pi environment for testing purposes.
"""

# Check if the current environment is a Raspberry Pi
if not is_raspberrypi():
    """
    If the current environment is not a Raspberry Pi,
    load the fake Raspberry Pi environment for testing.
    """
    load_fake_rpi()  # Load the fake Raspberry Pi environment
