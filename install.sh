#!/usr/bin/env bash
DATABASE_USERNAME="root"
DATABASE_PASSWORD="password"
CURRENT_DIR=$(pwd)

echo "****Installing Solarberry Monitor****"

echo "***Creating solarberrydb***"
mysql -u$DATABASE_USERNAME -p$DATABASE_PASSWORD < solarberrydb.sql

echo "***Creating cron job for periodically purging data***"
crontab -l > mycron
echo "0 */6 * * *  mysql -u$DATABASE_USERNAME -p$DATABASE_PASSWORD < $CURRENT_DIR/purge_solarberry_db.sql >> $CURRENT_DIR/db_purge.log 2>&1" >> mycron
crontab mycron
rm mycron

echo "***Enabling auto-start on boot***"
echo "TODO - This needs to be run manually right now, sorry!"
