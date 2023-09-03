import time
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import logging
from lib.component import Component
from settings import system_dict
from settings import settings_dict

# Configure logging
logger = logging.getLogger(__name__)


class StepperDriverError(Exception):
    """Custom exception for stepper driver-related errors."""

    def __init__(self, message):
        super().__init__(message)


class StepperDriver:
    """Class for managing the stepper motor driver in a 3D printing system."""

    def __init__(self, stopped_event):
        """Initialize the StepperDriver instance with default values."""
        self.__machine_stepping = settings_dict['machine']['stepping']
        self.__machine_accuracy_z = settings_dict['machine']['accuracy']['z']
        self.__machine_dimension_z = settings_dict['machine']['dimensions']['z']
        self.__acceleration_min_delay = settings_dict['print']['acceleration']['min_delay']
        self.__acceleration_max_delay = settings_dict['print']['acceleration']['max_delay']

        self.stopped = stopped_event
        self.disable()

    def enable(self):
        """Enable the stepper motor."""
        logger.debug(f"Enabling Stepper Motor")
        Component.off('motor_disabled')

    def disable(self):
        """Disable the stepper motor."""
        logger.debug(f"Disabling Stepper Motor")
        Component.on('motor_disabled')

    def end_stop_triggered(self):
        """Check if the end-stop limit switch is triggered.

        Returns:
            bool: True if triggered, False otherwise.
        """
        if Component.is_set('limit_switch'):
            logger.debug(f"End-Stop triggered")
            return True
        return False

    def set_direction(self, direction):
        """Set the direction of the stepper motor.

        Parameters:
            direction (str): "CW" for clockwise, "CCW" for counter-clockwise.

        Raises:
            ValueError: If the direction is not "CW" or "CCW".
        """
        if direction == "CW":
            logger.debug(f"Setting direction to CW (clock-wise)")
            Component.on('motor_direction')
        elif direction == "CCW":
            logger.debug(f"Setting direction to CCW (counter-clock-wise)")
            Component.off('motor_direction')
        else:
            raise ValueError("Direction must be either 'CW' or 'CCW'")

    def move_with_accel(self, steps, accel_rate=0.95):
        """Move the stepper motor with acceleration.

        Parameters:
            steps (int): Number of steps to move.
            accel_rate (float): Acceleration rate, defaults to 0.95.
        """
        logger.debug(f"Moving motor for {steps} steps with an acceleration of {accel_rate}")
        delay = self.__acceleration_max_delay
        half_steps = steps // 2

        # Acceleration
        for _ in range(half_steps):
            if self.end_stop_triggered():
                break
            self.step(1, delay)
            delay *= accel_rate
            if delay < self.__acceleration_min_delay:
                delay = self.__acceleration_min_delay

        # Deceleration
        for _ in range(steps - half_steps):
            if self.end_stop_triggered():
                break
            self.step(1, delay)
            delay /= accel_rate
            if delay > self.__acceleration_max_delay:
                delay = self.__acceleration_max_delay

    def step(self, steps, delay=0.001):
        """Perform a number of steps with the stepper motor.

        Parameters:
            steps (int): Number of steps to perform.
            delay (float): Delay between steps in seconds, defaults to 0.001s.

        Raises:
            StepperDriverError: If the printer is not leveled or calibrated.
        """
        for _ in range(steps):
            Component.on('motor_stepping')
            time.sleep(delay / 2)
            Component.off('motor_stepping')
            time.sleep(delay / 2)
            system_dict['motor_position'] += 1

    def up(self, steps):
        """Move the stepper motor up by a number of steps.

        Parameters:
            steps (int): Number of steps to move up.
        """
        logger.debug(f"Moving motor UP for {steps} steps")
        self.enable()
        self.set_direction('CW')
        self.move_with_accel(steps)
        self.disable()

    def down(self, steps):
        """Move the stepper motor down by a number of steps.

        Parameters:
            steps (int): Number of steps to move down.
        """
        logger.debug(f"Moving motor DOWN for {steps} steps")
        self.enable()
        self.set_direction('CCW')
        self.move_with_accel(steps)
        self.disable()

    def goto(self, pos):
        """Move the stepper motor to a specific position.

        Parameters:
            pos (int): The position to move to.

        Returns:
            bool: True if the move is successful, False otherwise.

        Raises:
            StepperDriverError: If the printer is not leveled or motor position is not set.
        """
        delta = system_dict['motor_position'] - pos
        logger.debug(f"Moving motor to Position {pos} (delta of {delta} steps)")

        if delta > 0:
            self.up(delta)
            return True
        elif delta < 0:
            self.down(delta)
            return True
        else:
            return True

    def level(self):
        """Level the stepper motor to the printing bed (position 0)."""
        logger.debug(f"Leveling to 0 (printing bed)")
        self.down(10000000000)
        system_dict['motor_position'] = 0
        system_dict['is_calibrated'] = True
        system_dict['calibration_time'] = datetime.now().time()

        # the limit observer thread is setting the stopped event if we reach the plate. Reset this.
        self.stopped.clear()