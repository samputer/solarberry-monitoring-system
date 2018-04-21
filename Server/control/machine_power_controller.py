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
import paramiko


class MachinePowerController:
    def __init__(self):
        logging.info("Creating " + str(self.__class__.__name__) + " object")
        self.__shutdown_list_file = '../Config/shutdownlist.txt'  # Change this file
        self.__ssh_user = 'pi'
        self.__ssh_pass = 'raspberry'
        self.__target_ip_addresses = self.read_target_ips_from_file()

    def read_target_ips_from_file(self):
        target_ip_addresses = []
        with open(self.__shutdown_list_file) as f:
            target_ip_addresses = f.readlines()
            # We have to read in the lines, then strip the newlines from it
            target_ip_addresses = [line.strip() for line in target_ip_addresses]
        f.close()

        logging.debug("Found the following IP addresses:")
        for idx, IP in enumerate(target_ip_addresses):
            logging.debug("IP " + str(idx + 1) + "- " + IP)
        return target_ip_addresses

    def shutdown_all(self, shutdown_time=60):
        for IP in self.__target_ip_addresses:
            self.shutdown(IP, shutdown_time, True)

    def shutdown(self, ip, shutdown_time, warn=True):
        logging.warn("Attempting to shutdown machine with IP:", ip)
        warning_command = 'zenity --error --title "Power Low"' \
                          ' --text "The SolarBerry is running low on battery power.\n\n ' \
                          'This machine will shutdown in 30 seconds.\n\n ' \
                          'Please save any open work." ' \
                          '--icon-name=battery' + str(
            shutdown_time) + ' second(s)"'
        shutdown_command = 'sudo shutdown -P +' + str(shutdown_time)
        full_command = shutdown_command
        ssh = paramiko.SSHClient()
        if warn:
            full_command = shutdown_command + warning_command
        logging.debug("Running command:", full_command)
        try:
            ssh.connect(ip, username=self.__ssh_user, password=self.__ssh_pass)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(full_command)
            if ssh_stdout | ssh_stderr:
                logging.info(ssh_stdout)
                logging.warn(ssh_stderr)
        except Exception as e:
            # TODO - Work out what exceptions this could throw
            logging.error(e)

