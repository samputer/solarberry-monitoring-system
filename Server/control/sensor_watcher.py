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

import threading
import logging
import time


class SensorWatcher:
    def __init__(self, sensors, demo=False):
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        self.__demo = demo
        self.__sensor_threads = dict()
        self.__sensors = sensors  # This is a dictionary of all of the sensors we are going to deal with
        self.__sensor_query_frequencies = self.get_query_frequencies()
        for sensor in self.__sensors:
            sensor_name = self.__sensors[sensor].get_name()
            sensor_key = self.__sensors[sensor].get_key()
            sensor_query_frequency = self.__sensor_query_frequencies[sensor_key]
            logging.info("Querying " + sensor_name + " every " + str(sensor_query_frequency) + " seconds")
            self.__sensor_threads[sensor] = threading.Thread(target=self.query_sensor_continuously,
                                                             args=(self.__sensors[sensor], sensor_query_frequency))
            self.__sensor_threads[sensor].daemon = True
            self.__sensor_threads[sensor].start()


    def get_query_frequencies(self):
        query_frequencies = dict()
        # Retrieve all of the identifiers for the sensors and put a default of 10
        for sensor, sensor_object in self.__sensors.iteritems():
            query_frequencies[self.__sensors[sensor].get_key()] = 10
        # If we're not in demo mode, overwrite what we just set
        if not self.__demo:
            # TODO Connect to the database and retrieve all of the poll frequency config options
            logging.debug("Querying the database for sensor query frequencies")
        return query_frequencies

    def query_sensor_continuously(self, sensor, sensor_query_frequency):
        while True:
            sensor.sense()
            time.sleep(sensor_query_frequency)
