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
from communications.websocket_handler import WebSocket
from control import controller_obj


class DataBroadcast(WebSocket):
    def handleConnected(self):
        logging.info("Somebody connected to the websocket - " + str(self.address))

    def handleClose(self):
        logging.info("Somebody disconnected from the websocket - " + str(self.address))

    def handleMessage(self):
        received_json = json.loads(str(self.data))
        logging.debug("Received a message")
        if 'ready' in received_json:
            logging.info("Sending them initial data")
            data_to_send = controller_obj.controller_obj.get_initial_data_to_send()
            logging.info("Sending them " + str(json.dumps(data_to_send)))
            self.sendMessage(str(json.dumps(data_to_send)))