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
    MonthName TEXT,
    MonthNumber INT,
    DayOfMonth INT,
    WeekOfYear INT,
    DayOfWeek TEXT,
    DayOfWeekNumber INT,
    Hour TEXT,
    HourInterval TEXT,


    PRIMARY KEY(
        (dayofweeknumber), monthnumber, dayofmonth, extractiondatetime, bikepointid
    )
);