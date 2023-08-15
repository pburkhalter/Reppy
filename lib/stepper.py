import time
from datetime import datetime, timedelta

import RPi.GPIO as GPIO
import logging

from main import gpio_dict
from settings import system_dict
from settings import settings_dict


class StepperDriverError(Exception):
    def __init__(self, message):
        super().__init__(message)


class StepperDriver:
    __machine_limit_switch = None
    
    __machine_stepping = None
    __machine_accuracy_z = None
    __machine_dimension_z = None

    __acceleration_min_delay = None
    __acceleration_max_delay = None

    def __int__(self):
        self.__machine_stepping = settings_dict['machine']['stepping']
        self.__machine_accuracy_z = settings_dict['machine']['accuracy']['z']
        self.__machine_dimension_z = settings_dict['machine']['dimensions']['z']

        self.__acceleration_min_delay = settings_dict['print']['acceleration']['min_delay']
        self.__acceleration_max_delay = settings_dict['print']['acceleration']['max_delay']

        # By default, disable the motor
        self.disable()

    def enable(self):
        logging.debug(f"Enabling Stepper Motor")
        GPIO.output(gpio_dict['motor_enabled'], GPIO.LOW)

    def disable(self):
        logging.debug(f"Disabling Stepper Motor")
        GPIO.output(gpio_dict['motor_enabled'], GPIO.HIGH)

    def end_stop_triggered(self):
        if GPIO.input(gpio_dict['limit_switch']):
            logging.debug(f"End-Stop triggered")
            return True
        return False

    def set_direction(self, direction):
        # direction: either "CW" for clockwise or "CCW" for counter-clockwise
        if direction == "CW":
            logging.debug(f"Setting direction to CW (clock-wise)")
            GPIO.output(gpio_dict['motor_direction'], GPIO.HIGH)
        elif direction == "CCW":
            logging.debug(f"Setting direction to CCW (counter-clock-wise)")
            GPIO.output(gpio_dict['motor_direction'], GPIO.LOW)
        else:
            raise ValueError("Direction must be either 'CW' or 'CCW'")

    def move_with_accel(self, steps, accel_rate=0.95):
        logging.debug(f"Moving motor for {steps} steps with an acceleration of {accel_rate}")
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

    def set_stepping(self, microsteps):
        # not used at the moment, because the board has separate micro-switches for setting the stepping
        if microsteps in [1, 2, 4, 8, 16]:
            settings = {
                1: (0, 0, 0),
                2: (1, 0, 0),
                4: (0, 1, 0),
                8: (1, 1, 0),
                16: (1, 1, 1)
            }.get(microsteps)
            for pin, value in zip(gpio_dict['motor_stepping'], settings):
                GPIO.output(pin, value)
        else:
            raise ValueError("Microsteps must be one of [1, 2, 4, 8, 16]")

    def step(self, steps, delay=0.001):
        if not system_dict['is_calibrated']:
            raise StepperDriverError("Printer is not leveled!")

        threshold_time = datetime.now() - timedelta(604800) # one week
        target_time = datetime.strptime(system_dict['calibration_time'], "%Y-%m-%d %H:%M:%S")
        if not target_time < threshold_time:
            raise StepperDriverError("Printer leveling seems to have happened over a week ago!")

        # Make the motor perform a number of steps.
        # steps: number of steps to perform
        # delay: delay between steps in seconds, defaults to 0.001s
        for _ in range(steps):
            GPIO.output(gpio_dict['motor_stepping'], GPIO.HIGH)
            time.sleep(delay / 2)
            GPIO.output(gpio_dict['motor_stepping'], GPIO.LOW)
            time.sleep(delay / 2)

            # update position
            system_dict['motor_position'] += 1

    def up(self, steps):
        logging.debug(f"Moving motor UP for {steps} steps")
        self.enable()
        self.set_direction('CW')
        self.move_with_accel(steps)
        self.disable()

    def down(self, steps):
        logging.debug(f"Moving motor DOWN for {steps} steps")
        self.enable()
        self.set_direction('CCW')
        self.move_with_accel(steps)
        self.disable()

    def position(self, pos):
        delta = system_dict['motor_position'] - pos
        logging.debug(f"Moving motor to Position {pos} (delta of {delta} steps)")

        if delta > 0:
            self.up(delta)
            return True
        elif delta < 0:
            self.down(delta)
            return True
        else:
            return True

    def level(self):
        logging.debug(f"Leveling to 0 (printing bed)")
        # reset position on z-axis
        self.down(10000000000)
        system_dict['motor_position'] = 0

        system_dict['is_calibrated'] = True
        system_dict['calibration_time'] = datetime.time()
