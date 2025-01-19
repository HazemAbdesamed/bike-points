\c `echo "$POSTGRES_HISTORICAL_DATA_DB"`

CREATE MATERIALIZED VIEW IF NOT EXISTS mvw_in_use_bikes_by_day 
AS

SELECT concat(day_of_week_number::VARCHAR, ': ', day_of_week) AS num_day_of_week, day_of_week, nb_empty_docks
FROM bike_points
