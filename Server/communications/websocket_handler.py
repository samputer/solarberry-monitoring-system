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
import signal
import threading
import json
import sys
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from communications.data_broadcast import DataBroadcast


class WebsocketHandler:
    def __init__(self, port=5678):
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        self.__port = port
        websocket_class = DataBroadcast  # the websocket class we're going to use
        self.__websocket_server_obj = SimpleWebSocketServer('', port, websocket_class)
        self.__websocket_server_thread = threading.Thread(target=self.start_websocket_server,
                                                          args=([self.__websocket_server_obj]))
        self.__websocket_server_thread.daemon = True
        self.__websocket_server_thread.start()
        signal.signal(signal.SIGINT,
                      self.close_sig_handler)  # This just makes sure that the sockets are closed tidily on program exit

    def broadcast(self, metric, value, level, timestamp):
        message = self.format_message_for_sending(metric, value, level, timestamp)
        connected_clients = self.__websocket_server_obj.connections.values()
        if len(connected_clients):
            logging.debug("Sending '" + str(message) + "' to " + str(len(connected_clients)) + " connected clients")
            for client in connected_clients:
                client.sendMessage(message)

    def format_message_for_sending(self, metric, value, level, timestamp):
        message = {'timestamp': timestamp, 'metric': metric, 'value': value, 'level': level}
        return json.dumps(message)

    def close_sig_handler(self, signal, frame):
        self.__websocket_server_obj.close()
        sys.exit()

    def start_websocket_server(self, server):
        logging.info("Starting websocket server on port " + str(self.__port))
        server.serveforever()
