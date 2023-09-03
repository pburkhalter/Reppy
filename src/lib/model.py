import logging
import os

from lib.unpack import Unpacker, UnpackerError
from lib.image import ImageProcessor, ImageProcessorError

# Configure logging
logger = logging.getLogger(__name__)

"""
This module provides a class for managing 3D models in a 3D printing system.
It uses custom Unpacker and ImageProcessor classes for file and image operations.
"""


class ModelError(Exception):
    """
    Custom exception for model-related errors.
    """

    def __init__(self, message):
        super().__init__(message)


class Model:
    """
    Class for managing 3D models in a 3D printing system.
    """

    def __init__(self, filepath=None):
        """
        Initialize the Model instance with default values.

        Parameters:
            filepath (str, optional): The file path of the 3D model.
        """
        self.images = {}
        self.config = {}
        self.filepath = filepath

        if self.filepath:
            self.load(filepath)

    def load(self, file_path=None):
        """
        Load a model from the provided file path.

        Parameters:
            file_path (str, optional): The file path of the 3D model.

        Returns:
            bool: True if the model is successfully loaded, False otherwise.
        """
        if file_path:
            self.filepath = file_path
        try:
            up = Unpacker(self.filepath)
            up.unpack()
            self.images = up.images
            self.config = up.config
        except UnpackerError as e:
            logger.error(f"Could not unpack model: {e}")
            return False

        self.extract_image_info()

    def extract_image_info(self):
        """
        Extract image information and validate images using ImageProcessor.

        Returns:
            bool: True if the image information is successfully extracted, False otherwise.

        Raises:
            ModelError: If the image processing fails.
        """
        try:
            for image in self.images:
                img = ImageProcessor(os.path.abspath(self.images[image]['filepath']))
                img.validate()

                self.images[image]['info'] = {
                    'resolution_x': img.resolution_x,
                    'resolution_y': img.resolution_y,
                    'aspect_ratio': img.aspect_ratio
                }
            return True
        except ImageProcessorError as e:
            raise ModelError(e)
