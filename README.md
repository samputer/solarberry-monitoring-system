#SolarBerry Monitoring System

The SolarBerry Monitoring System is a Raspberry Pi-based Monitoring Tool designed to report and educate on the state of the SolarBerry, an off-grid computer laboratory, currently under development in Malawi

_This project is currently a work-in-progress_

##Features

_TODO_

##Components:

###Server

This talks to the Arduino, requests data, broadcasts it out to front-end and logs to the db (Python)

###Arduino

This handles communication with the sensors and controls the LCD display (Arduino C)

###Front-end

This is the web front-end that displays all of this data and also links back to the educational content (JS/HTML/CSS)

##Additional Components

##SQL

DDL for the database

##Cron

Runs periodically and clears out the db (as every metric is logged, there will be a rapid build-up of data here)

##rc.local entries

Controls running on boot

##rtc/nts config

TODO - document this

##Installation - _This is a work in progress!!!_


###Step 1 - Create Database
```SQL
mysql -u root -P '<password>' < config/solarberrydb.sql
```

###Step 2 - Create Cron jobs
```bash
crontab -w ... TODO
```

###Step 3 - Setup rc.local entries
```
TODO
```

###Step 4 - Create symlink from web directory
```
ln -s <TODO>
```
##Troubleshooting

##Licensing

The SolarBerry Monitoring System is licensed under the GNU GPL. Please see `LICENSE.txt` for full details.

If this license is unsuited to your application, please contact the developer for alternative licensing options.
