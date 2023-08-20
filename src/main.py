import logging
import sys

from lib.threading import ThreadManager
from lib.limit import LimitSwitch

from settings import settings_dict
from print import PrintLoop
from api import APIController
from console import ConsoleHandler


logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configure logging
logger = logging.getLogger(__name__)


tm = ThreadManager()

tm.register("limit", LimitSwitch) # registering the z-axis limit switch observer (security)
tm.register("printer", PrintLoop) # registering the print manager

if settings_dict['system']['modules']['api'] == 'enabled':
    tm.register("api", APIController) # registering the flask REST API


if __name__ == "__main__":
    # starting registered threads
    tm.start()

    # entering console-loop (if enabled)
    if settings_dict['system']['modules']['console'] == 'enabled':
        ch = ConsoleHandler()
        ch.run()

