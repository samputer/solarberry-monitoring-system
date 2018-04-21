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
import time
from control.controller import Controller
import control.controller_obj


def main():
    # Sort out the logging config
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level="DEBUG")

    # Should we fake all sorts of things? (no db/no serial/no shutdown/no relay)
    demo_mode = True

    # Spin up our controller - this handles everything
    controller_obj.init()
    controller_obj.controller_obj = Controller(demo_mode)

    # We just need this to stop the main thread from completing
    while True:
        logging.info("Server is just fine & dandy!")
        time.sleep(10)


if __name__ == "__main__":
    main()
