\c `echo "$POSTGRES_HISTORICAL_DATA_DB"`

CREATE MATERIALIZED VIEW IF NOT EXISTS mvw_broken_docks_history 
AS

SELECT extraction_date, day_of_week, nb_broken_docks
FROM bike_points
ORDER BY extraction_date DESC