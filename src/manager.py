import logging
import os
import queue
import sys
import time

from lib.job import Job
from lib.stepper import StepperDriver


# Configure logging
logger = logging.getLogger(__name__)


class Manager:
    def __init__(self, queues, stop_signal):
        self.queues = queues
        self.stopped = stop_signal

        # Initialize the dictionary that maps strings to functions
        self.function_map = {
            "start": self.start,
            "stop": self.stop,
            "level": self.level,
            "exit": self.exit,
            "reboot": self.reboot
        }

    def handle(self, incoming_string, *args, **kwargs):
        """Main loop for the print process."""
        while True:
            try:
                cmd = self.queues['cmd'].get(timeout=2)
                # Look up the function in the dictionary
                func = self.function_map.get(cmd[0])

                # Call the function if it exists
                if func:
                    func(cmd[1])
                else:
                    logger.warning(f"No function mapped to the string '{incoming_string}'")
            except queue.Empty:
                time.sleep(1)

    def start(self, **kwargs):
        self.stopped.clear()

    def stop(self, **kwargs):
        self.stopped.set()

    def level(self, **kwargs):
        sd = StepperDriver(self.stopped)
        sd.level()

    def exit(self, **kwargs):
        sys.exit()

    def reboot(self, **kwargs):
        os.system('reboot')
