import logging

import RPi.GPIO as GPIO
from settings import settings_dict


# Configure logging
logger = logging.getLogger(__name__)


"""
Raspberry Pi 4B GPIO Pin Layout (https://github.com/tvierb/raspberry-ascii)
                            J8
                           .___.              
                  +3V3---1-|O O|--2--+5V
          (SDA)  GPIO2---3-|O O|--4--+5V
         (SCL1)  GPIO3---5-|O O|--6--_
    (GPIO_GLCK)  GPIO4---7-|O O|--8-----GPIO14 (TXD0)
                      _--9-|O.O|-10-----GPIO15 (RXD0)
    (GPIO_GEN0) GPIO17--11-|O O|-12-----GPIO18 (GPIO_GEN1)
    (GPIO_GEN2) GPIO27--13-|O O|-14--_
    (GPIO_GEN3) GPIO22--15-|O O|-16-----GPIO23 (GPIO_GEN4)
                  +3V3--17-|O O|-18-----GPIO24 (GPIO_GEN5)
     (SPI_MOSI) GPIO10--19-|O.O|-20--_
     (SPI_MISO) GPIO9 --21-|O O|-22-----GPIO25 (GPIO_GEN6)
     (SPI_SCLK) GPIO11--23-|O O|-24-----GPIO8  (SPI_C0_N)
                      _-25-|O O|-26-----GPIO7  (SPI_C1_N)
       (EEPROM) ID_SD---27-|O O|-28-----ID_SC Reserved for ID EEPROM
                GPIO5---29-|O.O|-30--_
                GPIO6---31-|O O|-32-----GPIO12
                GPIO13--33-|O O|-34--_
                GPIO19--35-|O O|-36-----GPIO16
                GPIO26--37-|O O|-38-----GPIO20
                      _-39-|O O|-40-----GPIO21
                           '---'
                       40W 0.1" PIN HDR

"""


GPIO_MODES = {
    "OUT": GPIO.OUT,
    "IN": GPIO.IN
}

GPIO_LEVELS = {
    "UP": GPIO.PUD_UP,
    "DOWN": GPIO.PUD_DOWN
}


class GPIOConfigError(Exception):
    def __init__(self, message):
        super().__init__(message)


class GPIOConfig:
    # Singleton
    _instance = None

    pins = {}
    board_revision = None

    def __int__(self):
        # set pin-layout to BCM
        GPIO.setmode(GPIO.BCM)

        # get the board revision
        self.board_revision = 3  # for local dev with fake pi
        # self.board_revision = GPIO.RPI_REVISION

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getitem__(self, key):
        if key in self.pins:
            return self.pins[key]
        else:
            raise KeyError(f"'{key}' not found")

    def set_pin(self, pin, mode, level=None):
        if mode not in GPIO_MODES:
            raise GPIOConfigError(f"GPIO Mode not found: {mode}")

        if mode == 'IN' and level not in GPIO_LEVELS:
            raise GPIOConfigError(f"GPIO Level not found: {level}")

        gpio_mode = GPIO_MODES.get(mode)
        gpio_level = {'pull_up_down': GPIO_LEVELS.get(level)} if GPIO_LEVELS.get(level) else {}

        try:
            GPIO.setup(pin, gpio_mode, **gpio_level)
        except Exception as e:
            raise GPIOConfigError(f"Error while setting GPIO Pin. Reason: {e}")

    def setup(self, pins):
        for name in pins:
            logger.info(f"Configuring Pin {pins[name].get('pin')} for {name}")
            self.set_pin(
                pins[name].get('pin'),
                pins[name].get('mode'),
                pins[name].get('level', None)
            )
            self.pins[name] = pins[name].get('pin')

    def cleanup(self):
        GPIO.cleanup()


gpio_dict = GPIOConfig()
gpio_dict.setup(settings_dict['gpio'])
