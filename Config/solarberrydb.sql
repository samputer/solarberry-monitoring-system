/*
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

*/



CREATE DATABASE solarberrydb;

USE solarberrydb;

CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'HighSchoolY4rds!';

GRANT INSERT,UPDATE,SELECT ON solarberrydb. * TO 'webuser'@'localhost';

FLUSH PRIVILEGES;

CREATE TABLE sun(
	logID int NOT NULL AUTO_INCREMENT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	metric VARCHAR(255),
	value FLOAT(8,3),
	level VARCHAR(255),
	PRIMARY KEY (logID)
);

CREATE TABLE input(
	logID int NOT NULL AUTO_INCREMENT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	metric VARCHAR(255),
	value FLOAT(8,3),
	level VARCHAR(255),
	PRIMARY KEY (logID)
);

CREATE TABLE battery(
	logID int NOT NULL AUTO_INCREMENT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	metric VARCHAR(255),
	value FLOAT(8,3),
	level VARCHAR(255),
	PRIMARY KEY (logID)
);

CREATE TABLE output(
	logID int NOT NULL AUTO_INCREMENT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	metric VARCHAR(255),
	value FLOAT(8,3),
	level VARCHAR(255),
	PRIMARY KEY (logID)
);

CREATE TABLE temperature(
	logID int NOT NULL AUTO_INCREMENT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	metric VARCHAR(255),
	value FLOAT(8,3),
	level VARCHAR(255),
	PRIMARY KEY (logID)
);

CREATE TABLE custom(
	logID int NOT NULL AUTO_INCREMENT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	metric VARCHAR(255),
	value text,
	level VARCHAR(255),
	PRIMARY KEY (logID)
);

CREATE INDEX sun_ts_metric on sun(timestamp,metric);
CREATE INDEX input_ts_metric on input(timestamp,metric);
CREATE INDEX battery_ts_metric on battery(timestamp,metric);
CREATE INDEX output_ts_metric on output(timestamp,metric);
CREATE INDEX temperature_ts_metric on temperature(timestamp,metric);
CREATE INDEX custom_ts_metric on custom(timestamp,metric);


CREATE TABLE thresholds(
	metric VARCHAR(255),
	level VARCHAR(255),
	min FLOAT(8,3),
	max FLOAT(8,3)
);

CREATE TABLE poll_frequencies(
	metric VARCHAR(255),
	poll_frequency int
);

INSERT INTO poll_frequencies VALUES('irradiance',10);
INSERT INTO poll_frequencies VALUES('current_in',10);
INSERT INTO poll_frequencies VALUES('voltage_in',1);
INSERT INTO poll_frequencies VALUES('battery_voltage',1);
INSERT INTO poll_frequencies VALUES('battery_percent',2);
INSERT INTO poll_frequencies VALUES('current_out',10);
INSERT INTO poll_frequencies VALUES('temperature_c',30);
INSERT INTO poll_frequencies VALUES('temperature_f',30);

INSERT INTO thresholds VALUES('irradiance','error',0,30);
INSERT INTO thresholds VALUES('irradiance','warning',30,75);
INSERT INTO thresholds VALUES('irradiance','ok',75,100);

INSERT INTO thresholds VALUES('current_in','error',-100,30);
INSERT INTO thresholds VALUES('current_in','warning',30,75);
INSERT INTO thresholds VALUES('current_in','ok',75,100);

INSERT INTO thresholds VALUES('voltage_in','error',0,9);
INSERT INTO thresholds VALUES('voltage_in','ok',9,12);
INSERT INTO thresholds VALUES('voltage_in','warning',12,100);

INSERT INTO thresholds VALUES('votlage_out','error',0,9);
INSERT INTO thresholds VALUES('voltage_out','ok',9,12);
INSERT INTO thresholds VALUES('voltage_out','warning',12,100);

INSERT INTO thresholds VALUES('battery_percent','error',0,15);
INSERT INTO thresholds VALUES('battery_percent','ok',15,60);
INSERT INTO thresholds VALUES('battery_percent','warning',60,100);

INSERT INTO thresholds VALUES('current_out','ok',-100,30);
INSERT INTO thresholds VALUES('current_out','warning',30,75);
INSERT INTO thresholds VALUES('current_out','error',75,100);

INSERT INTO thresholds VALUES('temperature_c','ok',0,30);
INSERT INTO thresholds VALUES('temperature_c','warning',30,75);
INSERT INTO thresholds VALUES('temperature_c','error',75,100);

INSERT INTO thresholds VALUES('temperature_f','ok',0,30);
INSERT INTO thresholds VALUES('temperature_f','warning',30,75);
INSERT INTO thresholds VALUES('temperature_f','error',75,100);



/*Remember to add a cron job to truncate this now and again as this data will rapidly build up!*/