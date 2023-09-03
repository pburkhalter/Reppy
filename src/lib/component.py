import RPi.GPIO as GPIO

from lib.gpio import gpio_dict

# Just for convenience, a class to manage GPIO components
class Component:

    @staticmethod
    def on(pin):
        # Turn on the GPIO pin if it's defined in gpio_dict
        if pin in gpio_dict:
            GPIO.output(gpio_dict[pin], GPIO.HIGH)

    @staticmethod
    def off(pin):
        # Turn off the GPIO pin if it's defined in gpio_dict
        if pin in gpio_dict:
            GPIO.output(gpio_dict[pin], GPIO.LOW)

    @staticmethod
    def is_set(pin):
        # Check if the GPIO pin is set (HIGH)
        if GPIO.input(pin) == GPIO.HIGH:
            return True
        return False

    @staticmethod
    def status(self):
        # Return the dictionary of GPIO pins and their values
        return gpio_dict
