\c `echo "$POSTGRES_HISTORICAL_DATA_DB"`

-- Create the BikePoints table
CREATE TABLE IF NOT EXISTS bike_points (
    bike_point_id TEXT,
    common_name TEXT,
    lat DECIMAL,
    lon DECIMAL,
    installed BOOLEAN,
    locked BOOLEAN,
    nb_bikes INT,
    nb_ebikes INT,
    nb_empty_docks INT,
    nb_docks INT,
    nb_broken_docks INT,
    extraction_datetime TIMESTAMP,
    extraction_date DATE,
    month_name TEXT,
    month_number INT,
    day_of_month INT,
    week_of_year INT,
    day_of_week TEXT,
    day_of_week_number INT,
    hour TEXT,
    hour_interval TEXT,

    -- Defining the primary key
    PRIMARY KEY (extraction_datetime, bike_point_id)
);

-- Create an index on DayOfWeekNumber
CREATE INDEX IF NOT EXISTS idx_day_of_week_number ON bike_points (day_of_week_number);

-- Create an index on DayOfMonth
CREATE INDEX IF NOT EXISTS idx_day_of_month ON bike_points (day_of_month);

-- Create stg_BikePoints table

CREATE TABLE IF NOT EXISTS stg_bike_points AS SELECT * FROM bike_points WHERE 1 <> 1
