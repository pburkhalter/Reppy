import time
import queue
import logging

from lib.task import TaskMessage
from lib.model import Model
from lib.stepper import StepperDriver, StepperDriverError
from lib.mask import Mask, MaskError

from settings import system_dict
from settings import settings_dict


# Configure logging
logger = logging.getLogger(__name__)


class PrintManager:
    queues = None
    task = None
    stepper = None
    mask = None

    __layer_current = None
    __layer_total = None

    def __init__(self, queues, stop_event):
        self.queues = queues
        self.stopped = stop_event
        self.loop()

        self.mask = Mask()
        self.model = Model()
        self.stepper = StepperDriver()

    def loop(self):
        while not self.stopped.is_set() or not self.queues['print'].empty():
            try:
                self.task = TaskMessage.deserialize(self.queues['print'].get(timeout=1))
                self.process()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in print loop: {e}")

    def process(self):
        task_id = self.task['id']
        task_recipient = self.task['recipient']
        task_command = self.task['command']
        task_data = self.task['data']

        if not (task_recipient == "print" and task_command == "PRINT"):
            return False

        logger.info(f"Processing print: {task_id}")

        if self.model.load(task_data['file_path']):
            # go to position 0 (printing bed)
            self.stepper.position(0)

            self.__layer_current = 0
            self.__layer_total = len(self.model.images)

            for index, (key, value) in enumerate(self.model.images):
                logger.info(f"Processing layer {self.__layer_current} of {self.__layer_total} "
                             f"({self.__layer_current} / {self.__layer_total}%)")

                # print bottom layers (over-exposure for plate-adhesion)
                while index <= settings_dict['print']['layer']['bottom']['layers']:
                    self.layer(
                        self.model.images[index]['filepath'],
                        settings_dict['print']['layer']['bottom']['height'],
                        settings_dict['print']['layer']['bottom']['exposure'],
                        settings_dict['print']['layer']['bottom']['blackout'],
                        settings_dict['print']['resin']['settling']
                    )

                # print remaining layers (default exposure)
                else:
                    self.layer(
                        self.model.images[index]['filepath'],
                        settings_dict['print']['layer']['default']['height'],
                        settings_dict['print']['layer']['default']['exposure'],
                        settings_dict['print']['layer']['default']['blackout'],
                        settings_dict['print']['resin']['settling']
                    )

    def layer(self, image, layer_height, exposure_time, blackout_time, settling):
        # move the motor up for the height of one layer
        self.stepper.up(layer_height)

        # wait for the resin to settle down
        time.sleep(settling)

        # load and display the exposure mask (image)
        self.mask.display(image)

        # turn on the uv-array for the defined amount of time
        self.mask.expose(exposure_time)

        # wait the specified blackout time
        time.sleep(blackout_time)

    @property
    def progress(self):
        return self.__layer_current / self.__layer_total
