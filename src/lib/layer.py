import time
import logging

from lib.stepper import StepperDriver, StepperDriverError
from lib.mask import Mask, MaskError

from settings import settings_dict


# Configure logging
logger = logging.getLogger(__name__)


class LayerManager:

    def __init__(self):
        self.model = None

        self.mask = Mask()
        self.stepper = StepperDriver()

        self.__layer_current = None
        self.__layer_total = None

    def load(self, model):
        self.model = model
        self.__layer_current = 0
        self.__layer_total = len(self.model.images)

        self.stepper.goto(0)

    def next(self):
        if self.__layer_current < self.__layer_total:
            self.layer(self.__layer_current)
            self.__layer_current += 1

    def layer(self, layer):
        logger.info(f"Processing layer: {layer}")

        # print bottom layer (over-exposure for plate-adhesion)
        if self.__layer_current <= settings_dict['print']['layer']['bottom']['layers']:
            self.process(
                self.model.images[layer]['filepath'],
                settings_dict['print']['layer']['bottom']['height'],
                settings_dict['print']['layer']['bottom']['exposure'],
                settings_dict['print']['layer']['bottom']['blackout'],
                settings_dict['print']['resin']['settling']
            )

        # print default layer (normal exposure)
        else:
            self.process(
                self.model.images[layer]['filepath'],
                settings_dict['print']['layer']['default']['height'],
                settings_dict['print']['layer']['default']['exposure'],
                settings_dict['print']['layer']['default']['blackout'],
                settings_dict['print']['resin']['settling']
            )

    def process(self, image, layer_height, exposure_time, blackout_time, settling):
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
    def current_layer(self):
        return self.__layer_current

    @property
    def total_layers(self):
        return self.__layer_total


