"""
                      \ | /
                    '-.;;;.-'
                   -==;;;;;==-
                    .-';;;'-.
                      / | \
                        '
 _____       _           ______
/  ___|     | |          | ___ \
\ `--.  ___ | | __ _ _ __| |_/ / ___ _ __ _ __ _   _
 `--. \/ _ \| |/ _` | '__| ___ \/ _ \ '__| '__| | | |
/\__/ / (_) | | (_| | |  | |_/ /  __/ |  | |  | |_| |
\____/ \___/|_|\__,_|_|  \____/ \___|_|  |_|   \__, |
Solarberry Monitoring System                    __/ |
by Sam Gray, 2018                              |___/

SolarBerry Monitoring System   Copyright (C) 2018  Sam Gray - www.sagray.co.uk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from __future__ import absolute_import

import logging
from RPi import GPIO as GPIO
import threading
import time


class Button:
    def __init__(self, gpio_pin, name='Button'):
        self.__name__ = name
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        self.__gpio_pin = gpio_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.__button_press_thread = threading.Thread(target=self.continually_check_for_button_press, args=())
        self.__button_press_thread.daemon = True
        self.__button_press_thread.start()

    def continually_check_for_button_press(self):
        while True:
            if GPIO.input(self.__gpio_pin) == 0:
                logging.info("Button " + self.__name__ + " pressed (GPIO" + str(self.__gpio_pin) + ")")
                self.perform_press_action()
                time.sleep(2)  # This is here so we don't trigger the action multiple times
            time.sleep(0.3)

    def perform_press_action(self):
        raise NotImplementedError("You need to override this method")
