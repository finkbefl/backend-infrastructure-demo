# backend-infrastructure-demo

Demo project of a backend infrastructure in python with kafka and faust for data-intensive real-time applications.

# Prerequisites

[Docker Desktop](https://docs.docker.com/desktop/) (tested with version 4.12.0) must be installed, or at least
- Docker (tested with version 20.10.20)
- Docker Compose (tested with version 2.10.2)

# Launch

To get the infrastructure running on a local machine, only the following steps are required:
1. Clone the repository
    ```
    git clone https://github.com/finkbefl/backend-infrastructure-demo.git
    ```
2. Launching the Docker infrastructure using the Docker Compose file
   ```
   docker compose -f "docker-compose.yaml" up -d --build
   ```

# Project Description

To build a flexible, scalable and fault-tolerant environment with low latency, the modern stream processing system Kafka will be used. The infrastructure is implemented with only one broker. Depending on the load on the productive system, distribution and replication can be implemented at any time using multiple brokers to increase the scalability and availability of the system.

The functionality of the backend is divided into small, isolated, event-driven microservices, which communicate asynchronously with Kafka through lean APIs. These microservices, encapsulated in individual Docker containers, are implemented using Python and can be integrated into the Kafka environment using the Faust library. The resulting increased security and ease of maintenance lead to a more complex deployment, which is why Docker Compose will be used. The microservices have the following roles:
- data_collection: Collect all raw sensor-data
- data_processing: Converting all sensor values to a common data type
- data_aggregation: Aggregate the data of the specific sensor number by calculating the average over the last 10 values
- db_loader: Load processed and aggregated data to the database

Test data in the form of temperature sensors can be simulated via a corresponding microservice and streamed into the system via the IoT-compliant MQTT protocol using a proxy. Separate topics correspond to the individual processing steps of the data and are to be monitored using Grafana and Prometheus.

The data from a Postgres database are provided to consumers through a REST API via an API gateway.

![Data_Infrastructure](.docs/../docs/assets/images/Data_Infrastructure.png)
Source: Own illustration based on Alaasam et al., 2019, Fig. 1

# Project Structure

TODO: Describe modules/files

├── aggregation  
│   ├── data_aggregation  
│   │   ├── main.py  
│   │   └── requirements.txt  
│   └── Dockerfile  
├── api-gateway  
│   ├── api_gateway  
│   │   ├── database.py  
│   │   ├── data_definition.py  
│   │   ├── main.py  
│   │   └── requirements.txt  
│   └── Dockerfile  
├── collection  
│   ├── data_collection  
│   │   ├── main.py  
│   │   └── requirements.txt  
│   └── Dockerfile  
├── config  
│   ├── grafana  
│   │   ├── dashboards  
│   │   │   └── services_dashboard.json  
│   │   └── provisioning  
│   │       ├── dashboards  
│   │       │   └── default.yaml  
│   │       └── datasources  
│   │           └── datasource.yaml  
│   ├── mqtt-broker  
│   │   └── mosquitto.conf  
│   └── prometheus  
│       └── prometheus.yaml  
├── docs  
│   └── assets  
│       └── images  
│           ├── Consumer_API.png  
│           └── Data_Infrastructure.png  
├── load  
│   ├── db_loader  
│   │   ├── database.py  
│   │   ├── data_definition.py  
│   │   ├── main.py  
│   │   └── requirements.txt  
│   └── Dockerfile  
├── processing  
│   ├── data_processing  
│   │   ├── main.py  
│   │   └── requirements.txt  
│   └── Dockerfile  
├── sensor-simulator  
│   ├── mqtt_proof_of_concept_scripts  
│   │   ├── publish.py  
│   │   └── subscribe.py  
│   ├── temp_sensors  
│   │   ├── main.py  
│   │   └── requirements.txt  
│   └── Dockerfile  
├── docker-compose.yaml  
├── LICENSE  
└── README.md  

# External Interfaces

- Grafana: `localhost:3000`  
  Initial login: user = admin, password = admin  
  The dashboard visualize
  - the number of data values received, processed and sent per min for the data_collection, data_processing and data_aggregation microservices
  - the number of values loaded into the database per min
  - the latency of the data values from the data simulation to the loading into the database
  - the number of REST API requests and the age of the requested last values
- Consumer API (Swagger UI): `localhost:8007/docs`  
  There are three HTTP GET methods implemented:
  - `/temperature`: Get all temperature values from the database for a specific sensor number between two timestamps
  - `/average`: Get all average values from the database for a specific sensor number between two timestamps
  - `/temperature_latest`: Get the latest available temperature value from the database for a specific sensor number
  ![Consumer_API](.docs/../docs/assets/images/Consumer_API.png)

# Used Sources

- Project is based on ideas from [microservice_in_python](https://github.com/KrasnovVitaliy/microservice_in_python) GitHub repository from [KrasnovVitaliy](https://github.com/KrasnovVitaliy)
- Sensor simulator is based on [Temperature-Sensor-Simulator](https://github.com/PrakashGudditi/Temperature-Sensor-Simulator/blob/master/cli2.py) GitHub repository from [PrakashGudditi](https://github.com/PrakashGudditi)

# Restrictions

- Demo project can be executed on a local machine. The deployment to a cloud is currently not considered.
- confluentinc/cp-kafka: Community licensed ([Docker Image Reference](https://docs.confluent.io/platform/current/installation/docker/image-reference.html))
- confluentinc/cp-kafka-mqtt: Commercially licensed ([Docker Image Reference](https://docs.confluent.io/platform/current/installation/docker/image-reference.html))
- Latency and age measurements depend on synchronisation of the different container-system-times (not an issue on a local machine)

# Status and Open Points

- Sensor simulation can be further extended by data variation and number of sensors (currently only one sensor streams integer temperature values every second)
- Microservice Implementations
  - Error handling must be extended
  - Unit Tests should be added
  - Performance of the system still has potential for improvement
- Security
  - Any kind of credentials must not be stored in the code, but for the sake of simplicity it is currently done like this
  - All communication channels should of course be encrypted for productive use (up to now unencrypted)
- API Gateway only provides data from the database via REST API
- Using multiple brokers on a productive system to increase the scalability and availability of the system

# Bibliography

> Alaasam, A. B. A., Radchenko, G., & Tchernykh, A. (2019). Stateful Stream Processing for Digital Twins: Microservice-Based Kafka Stream DSL. 2019 International Multi-Conference on Engineering, Computer and Information Sciences (SIBIRCON), 0804–0809. https://doi.org/10.1109/SIBIRCON48586.2019.8958367


