# EverCluster
This repository presents EverCluster, a cloud-based platform intended to make clustering workflow more straightforward and efficient. With EverCluster, users can set up clustering parameters, upload datasets, and get algorithm recommendations based on how well their algorithms perform across a range of criteria. Using machine learning models, the platform suggests clustering techniques based on user preferences for accuracy or speed. Furthermore, EverCluster is designed to function in a variety of deployment scenarios and provides versatility in single- and multi-node configurations.

It is recommended to read the EverCluster.pdf file for the comprehensive documentation.

## Code Structure
- [Current Directory](./.): The Thesis PDF, the License, and the README are all located in this directory. To deploy the platform with Docker or Docker Swarm, this directory also contains the docker-compose.yml file.
- [classification_model](./classification_model): The synthetic data (CSV files) needed to create the Random Forest ML models in the EverCluster Recommendation Component are contained in this directory. You can also get the code used to make the models here.
- [experimentation-data](./experimentation-data): The data utilized as experimentaion dataset are located in this directory. Every CSV file has values that are scaled from zero to one.
- [flask-server](./flask-server): This is the directory of the Server and User Interface components of EverCluster. Python code can be found and a corresponding Dockerfile. The entrypoint of the image is the `server.py`. Images used in the platform as well as all the differetn subcomponents of the Server can be found in this directory as well. Though the Docker Compose file the following subdirectories can be utilised for development perpuses as volumes.
- [spark-code](./spark-code): In this directory the Dockerfile used in order to create the Spark Nodes can be found. Though the Docker Compose file the following subdirectories can be utilised for development perpuses as volumes.
  - [spark-code/apps](./spark-code/apps): In this subdirectory the applications used by the Spark Master can be found.
  - [spark-code/data](./spark-code/data): This directory has example data for experimentation perpuses.

## Prerequisites
In order to deploy the platform you can use the following prerequisites to install it in single-node mode. In order to perform a multi-node installation changes are needed in the docker-compose.yml file.

### Single-Node Installation
- [Docker Engine](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)
- 8 CPU cores
- 8 GM RAM

The above can differ depending on your system.

## Installation
In a directory of your liking open a Terminal or a CMD and type the following
```shell
git clone https://github.com/karamolegkos/EverCluster.git
cd EverCluster
```

Now you are in the EverCluster main branch. Use the following command while Docker Engine is running to install EverCluster:
```shell
docker-compose up -d
```

After all the containers are up, you can access EverCluster from the following URL using a browser:
```
localhost:5000
```

## Uninstalling EverCluster
In order to uninstall EverCluster, from the same directory as the last command shown in the Installation phase, type the following using a Terminal or a CMD:
```
docker-compose down
```
