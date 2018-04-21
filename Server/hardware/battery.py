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
from datetime import datetime
from hardware.sensor import Sensor
from control import controller_obj

class Battery(Sensor):
    def __init__(self, name, key, serial_port, demo=False, battery_capacity=10000):
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        self.__battery_total_capacity = battery_capacity
        self.__battery_remaining_capacity = battery_capacity  # TODO Fix this to pull the most recent value, not 100%
        self.__last_battery_snapshot = {"current_in": datetime.now(), "current_out": datetime.now()}
        self.__set_battery_percentage()
        Sensor.__init__(self, name, key, serial_port, demo)

    def update(self, current_in_or_current_out, value):
        seconds_since_last_update = (
        datetime.now() - self.__last_battery_snapshot[current_in_or_current_out]).total_seconds()
        Ah_divisor = 3600 / seconds_since_last_update
        Ah_change = float(value) / Ah_divisor
        if current_in_or_current_out == 'current_in':
            self.__battery_remaining_capacity = self.__battery_remaining_capacity + Ah_change
        elif current_in_or_current_out == 'current_out':
            self.__battery_remaining_capacity = self.__battery_remaining_capacity - Ah_change
        self.__last_battery_snapshot[current_in_or_current_out] = datetime.now()

    def __set_battery_percentage(self):
        self.__battery_percent = float(100) / self.__battery_total_capacity * self.__battery_remaining_capacity

    def get_percentage(self):
        return self.__battery_percent

    def calibrate(self, value):
        logging.debug("Calibrating battery to", str(value) + "%")
        self.__battery_remaining_capacity = (100 / self.__battery_total_capacity) * value
        self.__set_battery_percentage()
        logging.debug("Battery % is now", str(self.get_percentage()) + "%")

    def get_capacity(self):
        return self.__battery_total_capacity

    def sense(self):
        # Cheat a little bit and just tell the controller that we found a result for this on the serial port
        controller_obj.found_result(self.get_key(), self.get_percentage())

