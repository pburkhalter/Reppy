import logging
import RPi.GPIO as GPIO

from lib.job import PrintJob
from lib.component import Component
from lib.gpio import gpio_dict

from settings import system_dict
from settings import settings_dict

# Configure logging
logger = logging.getLogger(__name__)

"""
This module provides a class for managing a limit switch in a 3D printing system.
It uses the RPi.GPIO library for GPIO operations and custom classes for job and component management.
"""


class LimitSwitch:
    """
    Class for managing a limit switch in a 3D printing system.
    """
    triggered = False
    limit_pin = False
    motor_pin = False

    def __init__(self, queues, stop_event):
        """
        Initialize the LimitSwitch instance with event queues and a stop event.

        Parameters:
            queues (Queue): The event queues for the system.
            stop_event (Event): The stop event for the system.
        """
        self.queues = queues
        self.stopped = stop_event
        self.limit_pin = gpio_dict['limit_switch']
        self.motor_pin = gpio_dict['motor_disabled']

        GPIO.add_event_detect(
            self.limit_pin,
            GPIO.FALLING,
            callback=self._switch_callback,
            bouncetime=200
        )

    def _switch_callback(self, channel):
        """
        Callback function to be executed when the limit switch is triggered.

        Parameters:
            channel (int): The GPIO channel that triggered the event.
        """
        Component.on('motor_disabled')
        self.triggered = True
        self.stopped.set()

    def is_triggered(self):
        """
        Check if the limit switch has been triggered.

        Returns:
            bool: True if the limit switch is triggered, False otherwise.
        """
        return self.triggered

    def reset(self):
        """
        Reset the trigger state. Call this after handling a trigger event.
        """
        self.triggered = False
        self.stopped.clear()

    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        GPIO.remove_event_detect(self.limit_pin)
