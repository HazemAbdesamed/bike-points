-- Create keyspace if not exists
CREATE KEYSPACE IF NOT EXISTS transportation
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Create table if not exists
CREATE TABLE IF NOT EXISTS transportation.metrics (
    min_extraction_datetime TIMESTAMP,
    max_extraction_datetime TIMESTAMP,
    nb_available_bikes INT,
    percentage_available_bikes DECIMAL,
    nb_available_ebikes INT,
    percentage_available_ebikes DECIMAL,
    nb_in_use_bikes INT,
    percentage_in_use_bikes DECIMAL,
    nb_broken_docks INT,
    percentage_broken_docks DECIMAL,

    PRIMARY KEY ((min_extraction_datetime, max_extraction_datetime))
 
) WITH default_time_to_live = 86400;  