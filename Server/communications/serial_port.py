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
import time
import Queue
import serial
import random
from control.controller_obj import controller_obj

class SerialPort:
    def __init__(self, serial_port="/dev/ttyUSB0", demo=False):
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        self.__demo = demo
        self.__baud_rate = 9600
        self.__serial_thread_lock = threading.Lock()
        self.__write_processing_speed = 5  # How often (secs) should we send our requests
        self.__serial_connection = None
        self.__queue = Queue.Queue()
        if not self.__demo:
            with self.__serial_thread_lock:
                print("WRITING INIT TO SERIAL")
                self.__serial_connection = serial.Serial(serial_port, self.__baud_rate)  # 9600 is the baud rate
                time.sleep(2)
                self.__serial_connection.write(
                    "init_10000_10_100")  # TODO - modify the Arduino code, this is no longer reqd

        time.sleep(10)
        serial_writer_thread = threading.Thread(target=self.continually_process_serial_write_queue,
                                                args=())
        serial_writer_thread.daemon = True
        serial_writer_thread.start()
        serial_reader_thread = threading.Thread(target=self.continually_process_serial_read_queue,
                                                args=())
        serial_reader_thread.daemon = True
        serial_reader_thread.start()

    def add_query(self, query):
        logging.debug("Adding query '" + str(query) + "' to serial port write queue")
        self.__queue.put(query)

    def continually_process_serial_write_queue(self):
        if not self.__demo:
            logging.debug("Beginning to process Serial port write queue")
            # Take any items at the front of the queue and write them to the serial port
            while not self.__queue.empty():
                queue_item = self.__queue.get(False)
                with self.__serial_thread_lock:
                    logging.debug("writing to serial port: '{towrite}'".format(towrite=queue_item))
                    self.__serial_connection.write(str.encode(queue_item+"\n"))
                    self.__serial_connection.flush()
        # we check the queue every 'n' seconds and process everything on it
        threading.Timer(self.__write_processing_speed, self.continually_process_serial_write_queue).start()

    def continually_process_serial_read_queue(self):
        if not self.__demo:
            with self.__serial_thread_lock:
                serial_response = self.__serial_connection.readline()
                bytes.decode(serial_response)
                print("*"+serial_response.rstrip()+"*")
                if serial_response.rstrip() != 'ready':
                    metric = bytes.decode(serial_response).rstrip().split(":")[0]
                    value = bytes.decode(serial_response).rstrip().split(":")[1]
                    controller_obj.controller_obj.found_result(metric, value)
        else:
            # If we're in demo mode...
            # Return a metric from the write queue and a random number
            if not self.__queue.empty():
                queue_item = self.__queue.get()
                logging.debug("Found a request for metric '" + queue_item + "'")
                controller_obj.found_result(queue_item, round(random.uniform(0, 99.9),2))

        threading.Timer(self.__write_processing_speed, self.continually_process_serial_read_queue).start()

