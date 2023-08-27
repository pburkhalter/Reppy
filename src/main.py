import logging
import os
import sys

from lib.thread import ThreadManager
from lib.limit import LimitSwitch

from settings import settings_dict
from print import PrintLoop
from api import APIController
from api.ws import WebSocketController


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(
                        os.path.join(settings_dict['system']['paths']['logging'], "application.log")),
                              logging.StreamHandler()])

# Configure logging
logger = logging.getLogger(__name__)

tm = ThreadManager()

tm.register("limit", LimitSwitch)  # registering the z-axis limit switch observer (security)
tm.register("printer", PrintLoop)  # registering the print manager

if settings_dict['system']['modules']['api'] == 'enabled':
    tm.register("api", APIController)  # registering the flask REST API

if settings_dict['system']['modules']['wsc'] == 'enabled':
    tm.register("wsc", WebSocketController)  # registering the websocket controller


if __name__ == "__main__":
    # starting registered threads
    tm.start()

