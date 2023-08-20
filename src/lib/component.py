import RPi.GPIO as GPIO

from lib.gpio import gpio_dict


# Just for convenience
class Component:

    @staticmethod
    def on(pin):
        if pin in gpio_dict:
            GPIO.output(gpio_dict[pin], GPIO.HIGH)

    @staticmethod
    def off(pin):
        if pin in gpio_dict:
            GPIO.output(gpio_dict[pin], GPIO.LOW)

    @staticmethod
    def is_set(pin):
        if GPIO.input(pin) == GPIO.HIGH:
            return True
        return False

    @staticmethod
    def status(self):
        return gpio_dict
