import time
import logging

from lib.task import TaskMessage
from lib.model import Model
from lib.stepper import StepperDriver, StepperDriverError
from lib.mask import Mask, MaskError

from settings import system_dict
from settings import settings_dict


class PrintManager:
    queue = None
    task = None
    sd = None
    ma = None

    __layer_current = None
    __layer_total = None

    def __init__(self, queue):
        self.queue = queue
        self.loop()

        self.md = Model()
        self.sd = StepperDriver()
        self.ma = Mask()

    def loop(self):
        # loop and wait for tasks...
        while True:
            if self.queue:
                self.task = TaskMessage.deserialize(self.queue.get())
                self.process()
            time.sleep(1)

    def process(self):
        task_id = self.task['id']
        task_recipient = self.task['recipient']
        task_command = self.task['command']
        task_data = self.task['data']

        if not (task_recipient == "print" and task_command == "PRINT"):
            return False

        logging.info(f"Processing print: {task_id}")

        if self.md.load(task_data['file_path']):
            # go to position 0 (printing bed)
            self.sd.position(0)

            self.__layer_current = 0
            self.__layer_total = len(self.md.images)

            for index, (key, value) in enumerate(self.md.images):
                logging.info(f"Processing layer: {self.__layer_current} of {self.__layer_total} "
                             f"({self.__layer_current} / {self.__layer_total}%)")

                # print bottom layers (over-exposure for plate-adhesion)
                while index <= settings_dict['print']['layer']['bottom']['layers']:
                    self.layer(
                        self.md.images[index]['filepath'],
                        settings_dict['print']['layer']['bottom']['height'],
                        settings_dict['print']['layer']['bottom']['exposure'],
                        settings_dict['print']['layer']['bottom']['blackout']
                    )

                # print remaining layers (normal exposure)
                if index > settings_dict['print']['layer']['bottom']['layers']:
                    self.layer(
                        self.md.images[index]['filepath'],
                        settings_dict['print']['layer']['default']['height'],
                        settings_dict['print']['layer']['default']['exposure'],
                        settings_dict['print']['layer']['default']['blackout']
                    )

    def layer(self, image, layer_height, exposure_time, blackout_time):
        # move the motor uf for the height of one layer
        self.sd.up(layer_height)

        # wait for the resin to settle down
        time.sleep(settings_dict['print']['resin']['settling'])

        # display the exposure mask (image)
        self.ma.display(image)

        # turn on the uv-array for the defined time
        self.ma.exposure(exposure_time)

        # wait the specified blackout time
        time.sleep(blackout_time)

        # move the motor up and down (retraction between layers)
        self.sd.up(settings_dict['print']['retraction']['height'])
        self.sd.down(settings_dict['print']['retraction']['height'])

    @property
    def progress(self):
        return self.__layer_current / self.__layer_total
