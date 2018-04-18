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
import threading
import pymysql.cursors


class MetricLogger:
    def __init__(self, demo=False):
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        self.__database_connection = None
        self.__database_connection_lock = threading.Lock()
        self.__demo = demo
        if not self.__demo:
            self.__database_connection = self.setup_database_connection()
        else:
            logging.warning("Running in DEMO mode - No metric logging will occur")

    def setup_database_connection(self):
        logging.info("Setting up logging database connection")
        dbConnection = pymysql.connect(host='localhost',
                                       user='root',
                                       password='passw0rd!',
                                       db='solarberrydb',
                                       charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)
        return dbConnection

    def log(self, metric_category, metric_name, metric_result, metric_level):
        if not self.__demo:
            with self.__database_connection.cursor() as cursor:
                sql = "INSERT INTO %s (`metric`, `value`, `level`) VALUES (%s, %s, %s)"
                with self.__database_connection_lock:
                    cursor.execute(sql, (metric_category, metric_name, metric_result, metric_level))
                    logging.debug("Ran Logging query: ", cursor._last_executed)
                self.__database_connection.commit()
