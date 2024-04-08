-- Create keyspace if not exists
CREATE KEYSPACE IF NOT EXISTS transportation
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};


-- Create table if not exists
CREATE TABLE IF NOT EXISTS transportation.bike_points (
    BikePointId TEXT,
    CommonName TEXT,
    Lat DECIMAL,
    Lon DECIMAL,
    Installed BOOLEAN,
    Locked BOOLEAN,
    NbBikes INT,
    NbEmptyDocks INT,
    NbDocks INT,
    NbEBikes INT,
    NbBrokenDocks INT,
    ExtractionDatetime TIMESTAMP,
    ExtractionDate DATE,
    WeekOfYear INT,
    DayOfWeek TEXT,

    PRIMARY KEY(
        (WeekOfYear, DayOfWeek),
        ExtractionDatetime, BikePointId
    )
);