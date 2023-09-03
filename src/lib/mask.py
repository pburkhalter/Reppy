import time
import pygame
import logging

from lib.component import Component
from settings import settings_dict

# Configure logging
logger = logging.getLogger(__name__)

"""
This module provides a class for managing the mask in a 3D printing system.
It uses the pygame library for image operations and custom Component class for hardware control.
"""


class MaskError(Exception):
    """
    Custom exception for mask-related errors.
    """

    def __init__(self, message):
        super().__init__(message)


class Mask:
    """
    Class for managing the mask in a 3D printing system.
    """

    def __init__(self):
        """
        Initialize the Mask instance with default values.
        """
        self.__hdmi_port = settings_dict['machine']['hdmi_port']
        pygame.init()
        self.screen = None
        self.setup_screen()

    def __del__(self):
        """
        Destructor to clean up resources.
        """
        pygame.quit()

    def setup_screen(self):
        """
        Set up the screen with specified display mode (full-screen).
        """
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, display=self.__hdmi_port)

    def get_screen_dimensions(self):
        """
        Get the dimensions of the screen.

        Returns:
            tuple: The width and height of the screen.
        """
        screen_info = pygame.display.Info()
        return screen_info.current_w, screen_info.current_h

    def load_image(self, image_path, width, height):
        """
        Load an image and scale it to the specified dimensions.

        Parameters:
            image_path (str): The file path of the image to be loaded.
            width (int): The width to scale the image to.
            height (int): The height to scale the image to.

        Returns:
            pygame.Surface: The scaled image.
        """
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (width, height))

    def display(self, image_path):
        """
        Display an image on the screen.

        Parameters:
            image_path (str): The file path of the image to be displayed.
        """
        width, height = self.get_screen_dimensions()
        scaled_image = self.load_image(image_path, width, height)
        self.screen.blit(scaled_image, (0, 0))
        pygame.display.flip()

    def expose(self, exposure_time):
        """
        Turn on the UV light source, wait for the exposure time, and turn it off.

        Parameters:
            exposure_time (float): The time for UV exposure in seconds.
        """
        Component.on('uv_enabled')
        time.sleep(exposure_time)
        Component.off('uv_enabled')
