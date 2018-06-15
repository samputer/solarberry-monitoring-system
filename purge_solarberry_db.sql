set @days_to_rollup=30;
set @rollup_interval_seconds=900;

DROP TEMPORARY TABLE IF EXISTS battery_rollup;

CREATE TEMPORARY TABLE battery_rollup
SELECT FROM_UNIXTIME(unix_timestamp(`timestamp`) - unix_timestamp(`timestamp`)%@rollup_interval_seconds) timestamp,
avg(value) as value,
metric
FROM battery
WHERE timestamp < CURRENT_DATE - INTERVAL @days_to_rollup DAY
GROUP BY timestamp, metric;

DELETE FROM battery
WHERE timestamp < CURRENT_DATE - INTERVAL @days_to_rollup DAY;

INSERT INTO battery(timestamp, metric, value)
SELECT timestamp, metric, value from battery_rollup;

-- TODO - Repeat this for all other metrics (it might be better in python after all)