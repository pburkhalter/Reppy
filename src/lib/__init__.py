import io
import sys

from utils.raspi import is_raspberrypi, load_fake_rpi


if not is_raspberrypi():
    load_fake_rpi()