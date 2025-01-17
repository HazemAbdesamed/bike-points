\c `echo "$POSTGRES_HISTORICAL_DATA_DB"`

-- Create the BikePoints table
CREATE TABLE IF NOT EXISTS transportation.public.BikePoints (
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

    -- Defining the primary key
    PRIMARY KEY (ExtractionDatetime, BikePointId)
);

-- Create an index on DayOfWeekNumber
CREATE INDEX IF NOT EXISTS idx_DayOfWeekNumber ON BikePoints (DayOfWeekNumber);

-- Create an index on DayOfMonth
CREATE INDEX IF NOT EXISTS idx_DayOfMonth ON BikePoints (DayOfMonth);
