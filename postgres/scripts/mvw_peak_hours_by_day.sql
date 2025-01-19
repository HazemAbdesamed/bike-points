\c `echo "$POSTGRES_HISTORICAL_DATA_DB"`

CREATE MATERIALIZED VIEW IF NOT EXISTS mvw_peak_hours_by_day 
AS

WITH day_hour_interval AS (
 SELECT day_of_week, day_of_week_number, hour_interval, hour, AVG(nb_empty_docks)::DECIMAL(4, 2) AS avg_nb_empty_docks
 FROM bike_points
 GROUP BY day_of_week, day_of_week_number, hour_interval, hour
)
, ordered AS (
 SELECT day_of_week, concat(day_of_week_number::VARCHAR, ': ', day_of_week) AS num_day_of_week, hour_interval, hour,
  avg_nb_empty_docks, dense_rank() OVER (PARTITION BY day_of_week ORDER BY avg_nb_empty_docks DESC) AS ord
 FROM day_hour_interval
)
SELECT day_of_week, num_day_of_week, hour_interval, avg_nb_empty_docks
FROM ordered
WHERE ord <= 3