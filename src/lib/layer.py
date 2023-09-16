import time
import logging

from lib.stepper import StepperDriver, StepperDriverError
from lib.mask import Mask, MaskError

from settings import settings_dict

# Configure logging
logger = logging.getLogger(__name__)

"""
This module provides a class for managing layers in a 3D printing process.
It uses custom StepperDriver and Mask classes for hardware control.
"""


class LayerManager:
    """
    Class for managing layers in a 3D printing process.
    """

    def __init__(self, stopped_event):
        """
        Initialize the LayerManager instance with default values.
        """
        self.model = None
        self.mask = Mask()
        self.stepper = StepperDriver(stopped_event)
        self.__layer_current = None
        self.__layer_total = None

    def load(self, model):
        """
        Load a model for printing and reset the current layer index.

        Parameters:
            model (object): The 3D model to be printed.
        """
        self.model = model
        self.__layer_current = list(self.model.images.keys())[0]
        self.__layer_total = len(self.model.images)
        self.stepper.goto(0)

    def next(self):
        """
        Move to the next layer if available.
        """
        if self.__layer_current < self.__layer_total:
            self.layer(self.__layer_current)
            self.__layer_current += 1

    def layer(self, layer):
        """
        Process a specific layer based on its index.

        Parameters:
            layer (int): The index of the layer to be processed.
        """
        logger.info(f"Processing layer: {layer}")

        if self.__layer_current <= settings_dict['print']['layer']['bottom']['layers']:
            self.process(
                self.model.images[layer]['filepath'],
                settings_dict['print']['layer']['bottom']['height'],
                settings_dict['print']['layer']['bottom']['exposure'],
                settings_dict['print']['layer']['bottom']['blackout'],
                settings_dict['print']['resin']['settling']
            )
        else:
            self.process(
                self.model.images[layer]['filepath'],
                settings_dict['print']['layer']['default']['height'],
                settings_dict['print']['layer']['default']['exposure'],
                settings_dict['print']['layer']['default']['blackout'],
                settings_dict['print']['resin']['settling']
            )

    def process(self, image, layer_height, exposure_time, blackout_time, settling):
        """
        Process a layer with the given parameters.

        Parameters:
            image (str): The file path of the image to be displayed.
            layer_height (float): The height of the layer.
            exposure_time (float): The time for UV exposure.
            blackout_time (float): The blackout time between layers.
            settling (float): The time for the resin to settle.
        """
        self.stepper.up(layer_height)
        time.sleep(settling)
        self.mask.display(image)
        self.mask.expose(exposure_time)
        time.sleep(blackout_time)

    @property
    def current_layer(self):
        """
        Get the current layer index.

        Returns:
            int: The current layer index.
        """
        return self.__layer_current

    @property
    def total_layers(self):
        """
        Get the total number of layers.

        Returns:
            int: The total number of layers.
        """
        return self.__layer_total
