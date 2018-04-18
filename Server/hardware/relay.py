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


class Relay:
    def __init__(self, name='Relay', gpio_pin=21):
        self.__name__ = name
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        self.__gpio_pin = gpio_pin
        self.__current_state = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__gpio_pin, GPIO.OUT)
        self.turn_on()

    def is_on(self):
        return self.__current_state

    def switch(self):
        if self.__current_state:
            self.turn_off()
        else:
            self.turn_on()

    def turn_on(self):
        if self.__current_state:
            logging.warn("Tried to turn ON a relay that is already ON (" + self.__name__ + ")")
        logging.warn("Turning on relay (" + self.__name__ + ")")
        GPIO.output(self.__gpio_pin, True)
        self.__current_state = True

    def turn_off(self):
        if not self.__current_state:
            logging.warn("Tried to turn OFF a relay that is already OFF (" + self.__name__ + ")")
        logging.warn("Turning off relay (" + self.__name__ + ")")
        GPIO.output(self.__gpio_pin, False)
        self.__current_state = False
