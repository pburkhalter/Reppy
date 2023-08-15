# only used for dev purposes
import lib.fake_rpi

import logging

from lib.threading import ThreadManager
from lib.print import PrintManager
from lib.limit import LimitSwitch
from lib.gpio import GPIOConfig
from api import create_app
from settings import settings_dict


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


gpio_dict = GPIOConfig()
gpio_dict.setup(settings_dict['gpio'])

tm = ThreadManager()

tm.register("limit", LimitSwitch) # registering the z-axis limit switch observer (security)
tm.register("api", create_app) # registering the flask REST API
tm.register("print", PrintManager) # registering the print manager


if __name__ == "__main__":
    # starting registered threads
    tm.start()
