# Introduction

A data engineering pipeline designed to **process**, **store**, and **analyze** London bike points data in both **near-real-time** and **historical layers**.

The system integrates:

- **Apache Kafka** and **Apache Spark** for processing and streaming,
- **Apache Cassandra** for storing historical data,
- **Trino** and **Superset** for visualizing insights,
- **Apache Airflow** for orchestrating the system.

The entire setup is containerized using **Docker**.

![Architecture](/Architecture.gif)

# The Data Source

This projects uses the **Transport for London (TfL) BikePoint API** to fetch data about bike points across Kindon. The API provides information such as bike availability, empty docks, total docks, and the geographic location of each bike point.

You can find more details about the API in this [link](https://api-portal.tfl.gov.uk/api-details#api=BikePoint&operation=BikePoint_GetAll).

## Sample API Response

When querying the endpoint [https://api.tfl.gov.uk/BikePoint/](https://api.tfl.gov.uk/BikePoint/), the API returns a JSON array containing objects for each bike point. Below is an sample of the structure:

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
      },..
    ]
  }
]
```

# Preprorcessing

The fields that have been extracted for this project are :
* **Id :** A unique identifier for each bike point.
* **commonName :** the name of the BikePoint.
* **Lat** and **Lon** Latitude and longitude values for the geographic location of the bike point
* **Lon :** the longitude coordinate of the bike point
* **Installed :** A boolean indicationg whether the bikepoint is installed.
* **Locked :** A boolean indicationg whether the bikepoint is locked.
* **NbDocks :** the total number of docks at the bike point
* **NbBikes :** the number of bikes at the bike point
* **NbEBikes :** the number of electric bikes at the bikepoint
* **NbEmptyDocks :** the number of empty docks (a dock without a bike) at the bike point
* **ExtractionDatetime :** a custom field added to indicate the time of the extraction.

Preprocessed data is then loaded into a kafka topic **bike-points**. This logic is implemented in this [folder](airflow/produce_to_kafka/), and is automated using an Airflow DAG **stage** that executes the preprocessing scripts every 3 minutes.

## Topics creation

To ensure the required Kafka topics are available, they are created during container's startup phase. This is achieved by the  [entrypoint.sh file](/kafka/config/entrypoint.sh), which executes the topic creation [script](/kafka/scripts/create-topics.sh) if the topics do not already exist.


# Processing

## Batch Layer
The Batch Layer is responsible for processing and storing historical data in an Apache Cassandra table. The schema for that table is found in this [file](/cassandra/scripts/init.cql).

The Primary Key should be carefully selected in Cassandra, it ensures the uniqueness of the record. It also determines the distribution of the data across nodes in the cluster and the order in which data is stored within each partition. The primar key is composed of the partition key, which is responsible for the distribution of data across nodes, and the clustering columns, which defines the order of data within each partition :
```
 PRIMARY KEY (
        (dayofweeknumber), monthnumber, dayofmonth, extractiondatetime, bikepointid
    )
```
*dayofweeknumber* is selected as a partition key as most of the historical queries are based onthe day of the week. The clustering keys *monthnumber*, *dayofmonth*, *extractiondatetime*, and *bikepointid* enable sorting data inside the partition.

The data in this layer originates from the preprocessed data stored in Kafka topic. The pipeling applies additional transformations to the data in spark, including :

* Generating new fields such as *MonthName*, *MonthNumber*, *DayOfWeek*, and *HourInterval*.
* Formatting and enriching data for efficient querying.

The processing logic is automated using an airflow DAG, which runs oncle daily at midnight.

## Speed Layer

The Speed Layer is designed to process near-real-time data and provide updated metrics quickly. Data is consumed from the preprocessing stage and processed using pyspark streaming.

The processing involves calculateing values for the metrics :

* The number of available bikes.
* The available bikes percentage.
* The number of available electric bikes.
* The available electric bikes percentage.
* The number of bikes that are in use.
* The percentage of the in use bikes.
* The number of broken docks.
* The percentage of broken docks.

These aggregated metrics are then published to a dedicated sink which is a kafka topic, which serves as the source for near-real-time analytics.

This processing is handled by a spark job and orchestrated through an airflow DAG.

### Airflow Container Setup
The airflow conatainer has been customized to enable communication with the Spark container and to manage job orchestration. Below are the key modifications :

#### **Dockerfile**
* Install the **sshpass** utility to facilitate SSH key distribution.
* Add an ssh config [file](/airflow/config/ssh_config).
* Include a [requirements.txt](/airflow/requirements.txt) file to install custom python dependencies.

#### **entrypoint.sh**
* Automatically creates an Airflow SSH connection if it does not already exist.
* Generate and send an SSH key to the SSH server.

### Spark Container Setup
The spark container has been customized to enable communication through ssh and execute the Spark jobs seamlessly.

#### **Dockerfile**
* Install and configure the SSH server to allow remote access.
* Add a spark user.
* Install python dependencies.

#### **entrypoint.sh**
* Configure the script to start the SSH server during container startup.

### Cassandra Container Setup
The Cassandra container has been customized to automate table creation during startup. The [entrpoint.sh file](/cassandra/config/entrypoint.sh) checks for the existence of the bike_points table and creates if it does not already exist. 

# Unified Layer

Trino DB serves as the query engine that unifies access to both the near-real-time and historical data layers. This is ensured by a table for each layer.

## Trino DB Container Setup
The Trino container has been configured to connect to both the Cassandra table and the Kafka metrics topic by preparing and including the necessary properties files the two files [cassandra.properties](/dashboard/config/cassandra.properties) and [kafka.properties](//dashboard/config/kafka.properties) contain information about the connection properties such as credentials, host names and ports, and table and topic names. These iles are placed inisde the /etc/trino/catalog directory.

# Dashboard

Trino DB tables are connected to the Superset dashboard, which provides a visual interface for data exploration. The dashboard is designed to showcase insights from both the near-real-time metrics and historical data.
The **bike points** dashboard showcases the insights through various charts :

### Real-Time metrics
Charts displaying the current values for each of the real-time metrics, including :

* Number and percentage of the available bikes.
* Number and percentage of available e-bikes.
* Number and percentage of empty docks.
* Number and percentage of broken docks.

These charts are automatically refreshed each 4 minutes.

### Historical Insights
- **Bikes in Use by Day of the Week:**  
  A bar chart showing the average number of in use bikes for the days of the week, helping identify usage patterns.

- **Bike Points Non-Availability:**  
  A heatmap displaying bike points' non-availability by day of the week. The x-axis represents days, while the y-axis represents the bike points with highest instances of non-availability. The metric represents the number of occurrences for when a bike point had no available bike by day.

- **Peak Hours:**  
  A heatmap showcasing the busiest hours for bike points, broken down by day of the week and time intervals. The metric represents the average number of empty docks by day and time interval. 

- **Broken Docks by Day of the Month:**  
  A Line chart illustrating the maximum number of broken docks over the previous days. 

![near-real-time metrics](/near-real-time%20metrics.jpg)
![historical charts](/Historical%20charts.jpg)

## Superset Container Setup
The Superset container has been customized to automate the initialization process and enable seamless integration with Trino.

#### **Dockerfile**
* Install the trino python library.
* Configure the container to use the [superset_init.sh](/dashboard/config/superset_init.sh) file as its entrypoint.
#### **superset_init.sh**
* Create the admin user with credentials defined in environment variables.
* Automatically import a preconfigured and customized dashboard from a [.zip](/dashboard/superset-dashboard-data.zip) file during container startup.

# Final Thoughts and Conclusion

This project demonstrates the integration of various technologies to design and implement a data pipeline capable of handling both batch and near-real-time processing by combining tools like Airflow, Kafka, Spark, Cassandra, Trino, and Superset.

## Key Takeaways:
- **Modular Design**: Each container was configured to handle specific tasks, ensuring seamless communication and functionality across the entire ecosystem.
- **Automation**: Tools like Airflow streamlined the orchestration of workflows, while customized container setups automated initialization processes and configurations.
- **Environment Variables for Flexibility**: Environment variables were extensively used across the setup to manage credentials and coniguration details. This approach simplifies updates, and ensures portability of the setup. 

## Furthur Enhancements:
While the current setup is functional and meets the project’s objectives, there are several areas for improvement to ensure greater reliability, security, and maintainability:
* Expand Airflow's monitoring capabilities to track the health and performance of all components in the setup, ensuring early detection and resolution of issues.
* Implementing data quality checks at each stage.
* Address potential security vulnerabilities.
* Adding more containers (nodes) for Kafka, Spark, and Cassandra to have a distributed architecture which will increase the system's scalability and resilience.

#
In conclusion, this project has provided valuable hands-on experience in data engineering, allowing me to explore and practice various tools and techniques. It serves as a solid foundation for future enhancements and scalability.<br>
**I appreciate your interest in following this journey !**
