import io
import sys

from utils.raspi import is_raspberrypi, load_fake_rpi

# Check if the current environment is a Raspberry Pi
if not is_raspberrypi():
    load_fake_rpi()  # Load the fake Raspberry Pi environment
