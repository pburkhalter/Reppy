import time
import pygame
import logging

from lib.component import Component
from settings import settings_dict

# Configure logging
logger = logging.getLogger(__name__)


class MaskError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Mask:
    def __init__(self):
        self.__hdmi_port = settings_dict['machine']['hdmi_port']

        pygame.init()

        self.screen = None
        self.setup_screen()

    def __del__(self):
        pygame.quit()

    def setup_screen(self):
        # Set display mode (full-screen)
        # The 'display' argument specifies which display to use (0 is the first display)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, display=self.__hdmi_port)

    def get_screen_dimensions(self):
        screen_info = pygame.display.Info()
        return screen_info.current_w, screen_info.current_h

    def load_image(self, image_path, width, height):
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (width, height))

    def display(self, image_path):
        width, height = self.get_screen_dimensions()
        scaled_image = self.load_image(image_path, width, height)

        self.screen.blit(scaled_image, (0, 0))
        pygame.display.flip()

    def expose(self, exposure_time):
        Component.on('uv_enabled')
        time.sleep(exposure_time)
        Component.off('uv_enabled')

