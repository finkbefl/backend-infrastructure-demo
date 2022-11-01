# backend-infrastructure-demo

Demo project of a backend infrastructure in python with kafka and faust for data-intensive real-time applications.
# Prerequisites

- [Docker Desktop](https://docs.docker.com/desktop/) (tested with version 4.12.0) must be istalled, or at least
  - Docker (tested with version 20.10.20)
  - Docker Compose (tested with version 2.10.2)
- Python 3.8+ (Faust requires Python 3.6 or later for the new async/await syntax, and variable type annotations)

# Restrictions

- Demo project can be executed on a local machine. The deployment to a cloud is currently not considered.
- confluentinc/cp-kafka: Community licensed ([Docker Image Reference](https://docs.confluent.io/platform/current/installation/docker/image-reference.html))
- confluentinc/cp-kafka-mqtt: Commercially licensed ([Docker Image Reference](https://docs.confluent.io/platform/current/installation/docker/image-reference.html))

# Project Structure

TBD

# Used Sources

- Project is based on ideas from [microservice_in_python](https://github.com/KrasnovVitaliy/microservice_in_python) GitHub repository from [KrasnovVitaliy](https://github.com/KrasnovVitaliy)


