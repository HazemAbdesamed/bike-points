# Introduction

A data engineering pipeline designed to **process**, **store**, and **analyze** London bike points data in both **near-real-time** and **historical layers**.

The system integrates:

- **Apache Kafka** and **Apache Spark** for processing.
- **Postgres** for storing historical data.
- **Apache Cassandra** for storing near-real-time data.
- **Trino** and **Apache Superset** for querying and visualizing insights.
- **Apache Airflow** for orchestrating the system.

The entire setup is containerized using **Docker**.

![Architecture](/pictures/architecture.gif)

# The Data Source

This projects uses the **Transport for London (TfL) BikePoint API** to fetch data about bike points across London. The API provides information such as the total number of docks, bike availability, empty docks, and the geographic location of each bike point.

You can find more details about the API in this [link](https://api-portal.tfl.gov.uk/api-details#api=BikePoint&operation=BikePoint_GetAll).

## Sample API Response

When querying the endpoint [https://api.tfl.gov.uk/BikePoint/](https://api.tfl.gov.uk/BikePoint/), the API returns a JSON array containing objects for each bike point. Below is an example of the structure:

```json
[
  {
    "id": "BikePoints_1",
    "commonName": "River Street , Clerkenwell",
    "lat": 51.529163,
    "lon": -0.10997,
    "additionalProperties": [
      {
        "$type": "Tfl.Api.Presentation.Entities.AdditionalProperties, Tfl.Api.Presentation.Entities",
        "category": "Description",
        "key": "NbBikes",
        "sourceSystemKey": "BikePoints",
        "value": "10",
        "modified": "2024-12-25T18:44:07.747Z"
      },
      {
        "$type": "Tfl.Api.Presentation.Entities.AdditionalProperties, Tfl.Api.Presentation.Entities",
        "category": "Description",
        "key": "NbEmptyDocks",
        "sourceSystemKey": "BikePoints",
        "value": "8",
        "modified": "2024-12-25T18:44:07.747Z"
      },
      {
        "$type": "Tfl.Api.Presentation.Entities.AdditionalProperties, Tfl.Api.Presentation.Entities",
        "category": "Description",
        "key": "NbDocks",
        "sourceSystemKey": "BikePoints",
        "value": "19",
        "modified": "2024-12-25T18:44:07.747Z"
      },....
    ]
  }
]
```

# Preprocessing

The fields that have been extracted for this project are :
* **Id :** A unique identifier for each bike point.
* **commonName :** The name of the bike point.
* **lat** and **lon :** Latitude and longitude values for the geographic location of the bike point.
* **Installed :** A boolean indicating whether the bike point is installed.
* **Locked :** A boolean indicating whether the bike point is locked.
* **NbDocks :** The total number of docks at the bike point.
* **NbBikes :** The number of bikes at the bike point.
* **NbEBikes :** The number of electric bikes at the bike point.
* **NbEmptyDocks :** The number of empty docks (docks without bikes or broken docks) at the bike point.
* **ExtractionDatetime :** A custom field added to indicate the time of the extraction.

Preprocessed data is then loaded into a kafka topic **bike-points**. This logic is implemented in this [folder](airflow/produce_to_kafka/), and is automated using an Airflow DAG **stage** that executes the preprocessing scripts every 3 minutes.

## Topic creation

To ensure the required Kafka topic is available, it is created during container's startup phase. This is achieved by the  [entrypoint.sh](/kafka/config/entrypoint.sh) file, which executes the topic creation [script](/kafka/scripts/create-topic.sh) if the topic does not already exist.

# Processing

## Batch Layer
The Batch Layer is responsible for processing and storing historical data in a Postgres table. The schema for that table is found in this [file](/postgres/scripts/create_tables_and_indexes.cql).

The Primary Key is used for the uniqueness of each record and indexing, it is defined as a combination of ***extraction_datetime*** and ***bike_point_id***
``` sql
  PRIMARY KEY (extraction_datetime, bike_point_id)
```

Indexes are implemented to optimize query performance, especially for filtering and aggregating data. In order to cater to the queries that commonly use filters and aggregations on ***day_of_week_number*** or ***day_of_month***, indexes have been created for these columns.
``` sql
  CREATE INDEX IF NOT EXISTS idx_day_of_week_number ON bike_points (day_of_week_number);
  CREATE INDEX IF NOT EXISTS idx_day_of_month ON bike_points (day_of_month);
```
In addtion, a staging table **stg_bike_points** is created in order to temporarily hold incoming data before it is loaded into the main table **bike_points**. This staging table helps identiy new data efficiently. 

The data in this layer originates from the preprocessed data stored in Kafka topic. The pipeline applies additional transformations to the data in Spark including : 
* Generating new fields such as ***MonthName***, ***MonthNumber***, ***DayOfWeek***, and ***HourInterval***.
* Formatting and enriching data for efficient querying.
* Loading into **stg_bike_points** which serves as an intermediate that will contain staged data which may contain duplicates or contains records that are already present in **bike_points**.

This data is then loaded into **bike_points** using the Postgres functionality **ON CONFLICT DO NOTHING**.

This script is found in this [file](/airflow/helpers/load_to_historical_data_table.sql)
```sql
INSERT INTO bike_points
SELECT *
FROM stg_bike_points

ON CONFLICT DO NOTHING;
```

To optimize query performance, materialized views that consume from the main table are created based on the specific queries executed by the dashboard. The scripts for creating these materialized views can be found in the following files:
* **mvw_in_use_bikes_by_day** : [/postgres/scripts/mvw_in_use_bikes_by_day.sql](/postgres/scripts/mvw_in_use_bikes_by_day.sql).
* **mvw_non_availability_by_day** : [/postgres/scripts/mvw_non_availability_by_day.sql](/postgres/scripts/mvw_non_availability_by_day.sql).
* **mvw_peak_hours_by_day** : [/postgres/scripts/mvw_peak_hours_by_day.sql](/postgres/scripts/mvw_peak_hours_by_day.sql).
* **mvw_broken_docks_history** : [/postgres/scripts/mvw_broken_docks_history.sql](/postgres/scripts/mvw_broken_docks_history.sql).

These materialized views are refreshed after loading the historical table **bike_points**.

The processing logic is automated using an Airflow DAG **load_batch**, which runs once daily at midnight.

![load_batch DAG](/pictures/load_batch%20DAG.jpg)


## Speed Layer

The Speed Layer is designed to process near-real-time data and provide updated metrics quickly. Data is consumed from the preprocessing stage and processed using PySpark streaming.

The processing involves calculating values for the metrics :

* The number and rate of available bikes.
* The number and rate of available electric bikes.
* The number and rate of bikes that are in use.
* The number and rate of broken docks.

These aggregated metrics are loaded then in a Cassandra table **metrics**, which serves as the source for near-real-time analytics.

This processing is handled by a Spark job and orchestrated through an Airflow DAG with the name **stream**.

### Airflow Container Setup
The airflow container has been customized to enable communication with the Spark container and to manage job orchestration. Below are the key modifications :

#### **Dockerfile**
* Install the **sshpass** utility to facilitate SSH key distribution.
* Add an ssh config [file](/airflow/config/ssh_config).
* Include a [requirements.txt](/airflow/requirements.txt) file to install custom python dependencies.

#### **entrypoint.sh**
* Automatically creates an Airflow SSH connection if it does not already exist.
* Generate and send an SSH key to the SSH server.

#### **entrypoint.sh**
* Create the topic that contains preprocessed data.
* Set the messages retention time for this topic to 48 hours.

### Spark Container Setup
The spark container has been customized to enable communication through ssh and execute the Spark jobs seamlessly.

#### **Dockerfile**
* Install and configure the SSH server to allow remote access.
* Add a spark user.
* Install python dependencies.

#### **entrypoint.sh**
* Configure the script to start the SSH server during container startup.

### Postgres Container Setup
The postgres container has been customized to automate table creation during startup. The [entrypoint.sh](/postgres/config/entrypoint.sh) file executes scripts inside */docker-entrypoint-initdb.d/* that create users, databases, tables, indexes, and materialized views if they don't exist. 

### Cassandra Container Setup
[/cassandra/scripts/init.cql](/cassandra/scripts/init.cql) is mounted on [/docker-entrypoint-initdb.d/](/docker-entrypoint-initdb.d/) in order to create the keyspace and table if they don't exist.

# Unified Layer
Trino serves as the query engine that unifies access to both the near-real-time and historical data layers.

## Trino Container Setup
The trino container has been configured to connect to both the postgres historical data table and the Cassandra metrics table by preparing the necessary properties files. The two files **[postgres.properties](/dashboard/config/postgres.properties)** and **[postgres.properties](/dashboard/config/cassandra.properties)** contain information about the connection properties such as credentials, host names and ports, and table names. These files are placed inisde the */etc/trino/catalog* directory inside the container. Also, a configuration is set to set the maximum number of concurrent queries that Trino can run to 4 in the [config.properties](/dashboard/config/config.properties) file. 

# Dashboard
Trino tables are connected to the Superset dashboard, which provides a visual interface for data exploration. The dashboard is designed to showcase insights from both the near-real-time metrics and historical data.
<br>

The **bike points** dashboard showcases the insights through various charts :

### Real-Time Metrics
Charts displaying the current values for each of the real-time metrics, including :

* Number and rate of the available bikes.
* Number and rate of available e-bikes.
* Number and rate of empty docks.
* Number and rate of broken docks.

These charts are automatically refreshed each 210 seconds in the Superest dashboard using a configuration that can be found inside the dashboard yaml file in [superset-dashboard-data.zip](/dashboard/superset-dashboard-data.zip) : 
``` yaml
refresh_frequency: 210
timed_refresh_immune_slices:
  - 7
  - 9
  - 11
  - 12
```

### Historical Insights
- **Bikes in Use by Day of the Week:** A bar chart showing the average number of in use bikes for the days of the week, helping identify usage patterns.

- **Bike Points Non-Availability:** A heatmap displaying bike points' non-availability by day of the week. The x-axis represents days, while the y-axis represents the bike points with highest instances of non-availability. The metric represents the number of occurrences for when a bike point had no available bike by day.

- **Peak Hours:** A heatmap showcasing the busiest hours for bike points, broken down by day of the week and time intervals. The metric represents the average number of empty docks by day and time interval. 

- **Broken Docks by Day of the Month:** A Line chart illustrating the maximum number of broken docks over the previous days. 

![near-real-time metrics](/pictures/near-real-time%20metrics.jpg)
![historical charts](/pictures/historical%20charts.jpg)

## Superset Container Setup
The superset container has been customized to automate the initialization process and enable seamless integration with Trino.

#### **Dockerfile**
* Install the trino python library.
* Install unzip and zip packages.
* Configure the container to use the [superset_init.sh](/dashboard/config/superset_init.sh) file as its entrypoint.
#### **superset_init.sh**
* Create the admin user with credentials defined in environment variables.
* Automatically import a preconfigured and customized dashboard from a [zip](/dashboard/superset-dashboard-data.zip) file during container startup.
#### **superset_config.py**
* Set the variable **SUPERSET_WEBSERVER_TIMEOUT** to 120 to prevent timeout errors, especially during the initial dashboard load.

# Requirements
- **Docker**
- **The setup might need around 6GB of memory.**

# Usage :
- Download the project.
- Navigate to the project folder on your machine.
- In a terminal, execute <code> docker-compose up --build -d </code>. The first exection will take some time as it will download the images and dependencies. The initial display of the dashboard will take some time for te reason that Trino will be planning the queries.
- You can enable the dags to run by the default schedule (the **stage** will be executed evey **3 minutes**, and the **load_batch** dag will be executed evey day at midnight) by enabling the toggle on switch. However if you want to trigger the dag manually, click on the play button.
![airflow usage](/pictures/airlfow%20usage.jpg)

# Final Thoughts and Conclusion

This project demonstrates the integration of various technologies to design and implement a data pipeline capable of handling both batch and near-real-time processing by combining tools like Docker, Airflow, Kafka, Spark, Postgres, Trino, and Superset.

## Some Key Takeaways:
- **Modular Design**: Each container was configured to handle specific tasks, ensuring seamless communication and functionality across the entire ecosystem.
- **Automation**: Tools like Airflow streamlines the orchestration of workflows, while customized container setups automated initialization processes and configurations.
- **Environment Variables for Flexibility**: Environment variables were extensively used across the setup to manage credentials and configuration details. This approach simplifies updates, and ensures portability of the setup. 

## Further Enhancements:
While the current setup is functional and meets the project’s objectives, there are several areas for improvement to ensure greater reliability, security, and maintainability:
* Expand Airflow's monitoring capabilities to track the health and performance of all components in the setup, ensuring early detection and resolution of issues.
* Implementing data quality checks at each stage.
* Address potential security vulnerabilities.
* Adding more containers (nodes) for Kafka, Spark, and postgres to have a distributed architecture which will increase the system's scalability and resilience.

# Conclusion
In conclusion, this project has provided valuable hands-on experience in data engineering, allowing me to explore and practice various tools and techniques. It serves as a solid foundation for future enhancements and scalability.<br>

**I appreciate your interest in following this journey !**
