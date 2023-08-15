import RPi.GPIO as GPIO

from lib.task import TaskMessage

from main import gpio_dict
from settings import system_dict
from settings import settings_dict


class LimitSwitch:
    triggered = False
    limit_pin = False
    motor_pin = False

    def __init__(self, queue):
        self.queue = queue

        self.limit_pin = gpio_dict['limit_switch']
        self.motor_pin = gpio_dict['motor_enabled']

        # Add an event detect on the falling edge (from HIGH to LOW) and specify the callback function.
        GPIO.add_event_detect(
            self.limit_pin,
            GPIO.FALLING,
            callback=self._switch_callback,
            bouncetime=200)

    def _switch_callback(self, channel):
        # Callback function to be executed when the limit switch is triggered.
        GPIO.output(self.motor_pin, GPIO.LOW)
        self.triggered = True

        tm = TaskMessage(
            recipient="ALL",
            command="EMERGENCY_STOP",
            message="Emergency-Stop (Limit-Switch)")
        self.queue.put(tm)

    def is_triggered(self):
        # Check if the limit switch has been triggered.
        return self.triggered

    def reset(self):
        # Reset the trigger state. Call this after handling a trigger event.
        self.triggered = False

    def cleanup(self):
        # Clean up GPIO resources.
        GPIO.remove_event_detect(self.limit_pin)
