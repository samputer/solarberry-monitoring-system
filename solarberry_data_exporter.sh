#!/usr/bin/env bash
export SOLARMONITORHOST=192.168.1.30;
export DBPASS=rachel;

echo "Saving all data from the SolarBerry Monitor to /tmp (enter password `rachel` when prompted)";
ssh pi@$SOLARMONITORHOST 'mysqldump -uroot -p$DBPASS --all-databases > /tmp/solarmonitordump.dmp';

echo "Step 2 - Copying the dump file across the network to your desktop - '/home/pi/Desktop/' (enter password `0p3n123!` when prompted)";
scp pi@$SOLARMONITORHOST:/tmp/solarmonitordump.dmp /home/pi/Desktop/;

echo "DONE - Now please manually copy the solarmonitordump.dmp file from your desktop onto a flash drive, and delete the file from the desktop"
