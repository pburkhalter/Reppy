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
        # Load a model for printing, reset current layer index
        self.model = model
        self.__layer_current = 0
        self.__layer_total = len(self.model.images)

        self.stepper.goto(0)

    def next(self):
        # Move to the next layer if available
        if self.__layer_current < self.__layer_total:
            self.layer(self.__layer_current)
            self.__layer_current += 1

    def layer(self, layer):
        logger.info(f"Processing layer: {layer}")

        # Print bottom layer (over-exposure for plate-adhesion)
        if self.__layer_current <= settings_dict['print']['layer']['bottom']['layers']:
            self.process(
                self.model.images[layer]['filepath'],
                settings_dict['print']['layer']['bottom']['height'],
                settings_dict['print']['layer']['bottom']['exposure'],
                settings_dict['print']['layer']['bottom']['blackout'],
                settings_dict['print']['resin']['settling']
            )

        # Print default layer (normal exposure)
        else:
            self.process(
                self.model.images[layer]['filepath'],
                settings_dict['print']['layer']['default']['height'],
                settings_dict['print']['layer']['default']['exposure'],
                settings_dict['print']['layer']['default']['blackout'],
                settings_dict['print']['resin']['settling']
            )

    def process(self, image, layer_height, exposure_time, blackout_time, settling):
        # Move the motor up for the height of one layer
        self.stepper.up(layer_height)

        # Wait for the resin to settle down
        time.sleep(settling)

        # Load and display the exposure mask (image)
        self.mask.display(image)

        # Turn on the UV-array for the defined amount of time
        self.mask.expose(exposure_time)

        # Wait the specified blackout time
        time.sleep(blackout_time)

    @property
    def current_layer(self):
        return self.__layer_current

    @property
    def total_layers(self):
        return self.__layer_total
