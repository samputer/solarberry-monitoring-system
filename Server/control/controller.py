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
import json
from datetime import datetime
from hardware.relay import Relay
from hardware.battery import Battery
from hardware.calibrate_button import CalibrateButton
from hardware.relay_override_button import RelayOverrideButton
from hardware.graph1 import Graph1
from hardware.sensor import Sensor
from control.sensor_watcher import SensorWatcher
from communications.serial_port import SerialPort
from communications.metric_logger import MetricLogger
from communications.websocket_handler import WebsocketHandler
from control.machine_power_controller import MachinePowerController


class Controller:
    def __init__(self):
        logging.info("Welcome to The Solar Monitoring System for the SolarBerry")

    def start(self, demo=True):
        logging.info("Starting the Controller")
        self.relay_obj = Relay("main_relay", 21)
        self.metric_logger_obj = MetricLogger(demo)  # True puts this into demo mode
        self.machine_power_controller_obj = MachinePowerController()
        self.calibrate_button_obj = CalibrateButton()
        self.relay_override_button_obj = RelayOverrideButton()
        self.serial_port_obj = SerialPort("/dev/ttyUSB0", demo)

        # Define all of our sensors hooked upto the arduino
        self.sensors = dict()  # a dictionary to hold references to all of our sensors
        self.sensors["current_in"] = Sensor("Panel Current", "current_in", self.serial_port_obj, demo)
        self.sensors["current_out"] = Sensor("Output Current", "current_out", self.serial_port_obj, demo)
        self.sensors["voltage_in"] = Sensor("Panel Voltage", "voltage_in", self.serial_port_obj, demo)
        self.sensors["voltage_out"] = Sensor("Output Voltage", "voltage_out", self.serial_port_obj, demo)
        self.sensors["temperature_c"] = Sensor("Temperature in C", "temperature_c", self.serial_port_obj, demo)
        # Our battery object tracks the percentage of the battery
        self.sensors["battery_percent"] = Battery("battery_percent", "battery_percent", self.serial_port_obj, demo,
                                                  1000)  # TODO Change this to an accurate battery size (should probably be a param)
        self.sensors["graph1"] = Graph1("graph1", "graph1", self.serial_port_obj, demo)

        self.websocket_handler_obj = WebsocketHandler(5678)

        # This fella deals with running the sensor's sense() function at specified intervals in their own threads
        self.sensor_watcher_obj = SensorWatcher(self.sensors, demo)

    def found_result(self, metric, value):

        # This guy is called by the serial port object any time a result is retrieved
        now = datetime.utcnow().isoformat() + 'Z'

        # Retrieve the lvel that the value equates to
        level = self.sensors[metric].get_level(value)

        # Put the result onto the sensor object
        self.sensors[metric].add_result(value, level, now)

        # If we've found a result for either of the current metrics, then use them to update the battery status
        if metric == 'current_in' or metric == 'current_out':
            self.sensors['battery_percent'].update(metric, value)

        # Now broadcast the value across to all of our connected clients
        self.websocket_handler_obj.broadcast(metric, value, level, now)

    def get_initial_data_to_send(self):
        # Loop through all of our sensor objects and ask them all to give us everything they have
        total_sensor_data = {"initial": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        logging.debug("Looping through " + str(len(self.sensors)) + " sensors to get all of their data")
        for sensor in self.sensors:
            sensor_data = self.sensors[sensor].get_all_data()
            total_sensor_data[self.sensors[sensor].get_key()] = json.dumps(sensor_data)
        graph1_data = self.sensors['graph1'].get_all_data()
        total_sensor_data['graph1'] = json.dumps(graph1_data)

        return total_sensor_data

