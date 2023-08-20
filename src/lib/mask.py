import time
import pygame
import sys
import logging

from lib.component import Component


# Configure logging
logger = logging.getLogger(__name__)


class MaskError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Mask:
    def __init__(self):
        pygame.init()

    def __del__(self):
        pygame.quit()

    def get_screen_dimensions(self):
        screen_info = pygame.display.Info()
        return screen_info.current_w, screen_info.current_h

    def load_and_scale_image(self, image_path, width, height):
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (width, height))

    def display_image(self, image, width, height):
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        screen.blit(image, (0, 0))
        pygame.display.flip()

    def display(self, image_path):
        width, height = self.get_screen_dimensions()
        scaled_image = self.load_and_scale_image(image_path, width, height)
        self.display_image(scaled_image, width, height)

    def expose(self, exposure_time):
        Component.on('uv_enabled')
        time.sleep(exposure_time)
        Component.off('uv_enabled')

