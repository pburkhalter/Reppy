import RPi.GPIO as GPIO

from lib.gpio import gpio_dict

"""
This module provides a convenient way to manage GPIO components on a Raspberry Pi.
It uses the RPi.GPIO library for GPIO operations and a custom gpio_dict for pin mappings.
"""


class Component:
    """
    A class to manage GPIO components on a Raspberry Pi.
    """

    @staticmethod
    def on(pin):
        """
        Turn on the GPIO pin if it's defined in gpio_dict.

        Parameters:
            pin (int or str): The pin identifier as defined in gpio_dict.

        Returns:
            None
        """
        if gpio_dict[pin]:
            GPIO.output(gpio_dict[pin], GPIO.HIGH)

    @staticmethod
    def off(pin):
        """
        Turn off the GPIO pin if it's defined in gpio_dict.

        Parameters:
            pin (int or str): The pin identifier as defined in gpio_dict.

        Returns:
            None
        """

        if gpio_dict[pin]:
            GPIO.output(gpio_dict[pin], GPIO.LOW)

    @staticmethod
    def is_set(pin):
        """
        Check if the GPIO pin is set (HIGH).

        Parameters:
            pin (int or str): The pin identifier as defined in gpio_dict.

        Returns:
            bool: True if the pin is set (HIGH), False otherwise.
        """

        if GPIO.input(gpio_dict[pin]) == GPIO.HIGH:
            return True
        return False

    @staticmethod
    def status(self):
        """
        Return the dictionary of GPIO pins and their values.

        Returns:
            dict: The gpio_dict containing pin mappings and their values.
        """
        return gpio_dict
