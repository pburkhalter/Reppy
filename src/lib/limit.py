import logging
import RPi.GPIO as GPIO

from lib.job import PrintJob
from lib.component import Component
from lib.gpio import gpio_dict

from settings import system_dict
from settings import settings_dict


# Configure logging
logger = logging.getLogger(__name__)


class LimitSwitch:
    triggered = False
    limit_pin = False
    motor_pin = False

    def __init__(self, queues, stop_event):
        self.queues = queues
        self.stopped = stop_event

        self.limit_pin = gpio_dict['limit_switch']
        self.motor_pin = gpio_dict['motor_disabled']

        # Add an event detect on the falling edge (from HIGH to LOW) and specify the callback function.
        GPIO.add_event_detect(
            self.limit_pin,
            GPIO.FALLING,
            callback=self._switch_callback,
            bouncetime=200)

    def _switch_callback(self, channel):
        # Callback function to be executed when the limit switch is triggered.
        Component.on('motor_disabled')
        self.triggered = True
        self.stopped.set()

    def is_triggered(self):
        # Check if the limit switch has been triggered.
        return self.triggered

    def reset(self):
        # Reset the trigger state. Call this after handling a trigger event.
        self.triggered = False
        self.stopped.clear()

    def cleanup(self):
        # Clean up GPIO resources.
        GPIO.remove_event_detect(self.limit_pin)
