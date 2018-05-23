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


class Graph1(Sensor):
    def __init__(self, name, key, serial_port, demo=False, battery_capacity=10000):
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        Sensor.__init__(self, name, key, serial_port, demo)

    def sense(self):
        # Just loop through all of the other sensors, take the current timestamp and put their most recent values into a fict
        all_sensors = controller_obj.sensors
        current_datetime = datetime.now()
        graph_data_snapshot = {}
        for sensor in all_sensors:
            sensor_key = sensor.get_key()
            if sensor_key != 'graph1':
                graph_data_snapshot[sensor_key] = sensor.get_all_data()


        # Cheat a little bit and just tell the controller that we found a result for this on the serial port
        controller_obj.controller_obj.found_result(self.get_key(), graph_data_snapshot)


