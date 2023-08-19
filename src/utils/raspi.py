import io
import logging
import sys


# Configure logging
logger = logging.getLogger(__name__)


# https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except (FileNotFoundError, PermissionError, IOError) as e:
        pass
    return False


def load_fake_rpi():
    logger.debug("Seems like we're not running on a raspberry pi. Loading Fake RPi.GPIO...")

    # Replace libraries by fake ones
    import fake_rpi

    sys.modules['RPi'] = fake_rpi.RPi  # Fake RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO  # Fake GPIO
    sys.modules['smbus'] = fake_rpi.smbus  # Fake smbus (I2C)

    # by default, it prints everything to std.error
    fake_rpi.toggle_print(True)  # turn on/off printing