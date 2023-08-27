import logging
from PIL import Image, UnidentifiedImageError, ImageOps

from settings import settings_dict


# Configure logging
logger = logging.getLogger(__name__)


class ImageProcessorError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ImageProcessor:
    __machine_resolution_x = None
    __machine_resolution_y = None
    __machine_aspect_ratio = None

    file = None
    image = None

    resolution_x = None
    resolution_y = None
    aspect_ratio = None

    def __init__(self, file_path=None):
        self.__machine_resolution_x = settings_dict['machine']['resolution']['x']
        self.__machine_resolution_y = settings_dict['machine']['resolution']['y']
        self.__machine_aspect_ratio = self.__machine_resolution_x / self.__machine_resolution_y

        if file_path:
            self.file = file_path
            self.open()
            self.extract_properties()

    def open(self, file_path=None):
        if file_path:
            self.file = file_path
        try:
            self.image = Image.open(self.file)
            self.image.load() # force pillow to load the image into memory
        except (FileNotFoundError, PermissionError, UnidentifiedImageError) as e:
            raise ImageProcessorError(f"Error opening the image at '{self.file}': {e}")

    def extract_properties(self):
        width, height = self.image.size

        self.resolution_x = width
        self.resolution_y = height
        self.aspect_ratio = self.resolution_x / self.resolution_y

    def grayscale(self):
        # Convert the image to grayscale
        grayscale_image = ImageOps.grayscale(self.image)

        # Check if the original image and the grayscale converted image are equal
        if not self.image == grayscale_image:
            self.image = grayscale_image

    def validate(self, to_grayscale=True):
        if not self.resolution_x == self.__machine_resolution_x:
            logger.error("Image resolution width (x) does not match.")
            raise ImageProcessorError("Image resolution width (x) does not match.")
        if not self.resolution_y == self.__machine_resolution_y:
            logger.error("Image resolution height (y) does not match.")
            raise ImageProcessorError("Image resolution height (y) does not match.")
        if not self.aspect_ratio == self.__machine_aspect_ratio:
            logger.error("Could not extract properties.")
            raise ImageProcessorError("Could not extract properties.")

        if to_grayscale:
            self.grayscale()
