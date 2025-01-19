\c `echo "$POSTGRES_HISTORICAL_DATA_DB"`

CREATE MATERIALIZED VIEW IF NOT EXISTS mvw_non_availability_by_day
AS

WITH most_non_available_bikepoints AS (
  SELECT bike_point_id, COUNT(bike_point_id) nb
  FROM bike_points
  WHERE nb_bikes = 0
  GROUP BY bike_point_id
  ORDER BY nb DESC
  LIMIT 10
)
SELECT DISTINCT concat(b.day_of_week_number::VARCHAR, ': ', b.day_of_week) AS num_day_of_week,
       b.extraction_date, b.bike_point_id
FROM bike_points b
INNER JOIN most_non_available_bikepoints m ON b.bike_point_id = m.bike_point_id 