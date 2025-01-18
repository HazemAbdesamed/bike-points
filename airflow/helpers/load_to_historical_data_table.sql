INSERT INTO bike_points
SELECT *
FROM stg_bike_points

ON CONFLICT DO NOTHING;