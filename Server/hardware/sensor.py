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
import logging
import pymysql.cursors
import collections


class Sensor:
    def __init__(self, name, key, serial_port, demo=False):
        logging.info("Creating " + str(self.__class__.__name__) + " object (" + name + ")")
        self.__name__ = name
        self.__demo = demo
        self.__key = key  # The key is what is sent to the Arduino tro request a metric
        self.__levels = self.get_metric_levels()
        self.__serial_port = serial_port
        self.__results = collections.deque([], 100)

    def setup_database_connection(self):
        logging.info("Setting up metric levels database connection")
        dbConnection = pymysql.connect(host='localhost',
                                       user='root',
                                       password='passw0rd!',
                                       db='solarberrydb',
                                       charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)
        return dbConnection

    def get_key(self):
        return self.__key

    def get_name(self):
        return self.__name__

    def get_metric_levels(self):
        levels = {'danger': {'min': 0, 'max': 50},
                  'warning': {'min': 51, 'max': 75},
                  'ok': {'min': 76, 'max': 9999}}
        if not self.__demo:
            # Query the database and cache all of the levels associated with this metric
            database_connection = self.setup_database_connection()
            with database_connection.cursor() as cursor:
                sql = "select level, min, max from thresholds where metric = %s"
                cursor.execute(sql, self.__name__)
                results = cursor.fetchall()
            for row in results:
                levels[self.__name__] = {'min': row['min'], 'max': row['max']}
        return levels

    def get_level(self, value):
        level = ''
        for key in self.__levels:
            if self.__levels[key]['min'] <= value <= self.__levels[key]['max']:
                level = key
                break
        return level

    def add_result(self, value, level, timestamp):
        logging.debug("adding result")
        self.__results.append({"timestamp": timestamp, "value": value, "level": level})

    def get_all_data(self):
        all_data = list(self.__results)
        return all_data

    def sense(self):
        self.__serial_port.add_query(self.__key)
