**IN DEVELOPMENT NOT READY FOR WIDE SPREAD USE YET**

# MyHero Ernst Service

This is the Vote Processing Service for a basic microservice demo application.
This service subscribes to an MQTT Server where votes are waiting for processing.

Details on deploying the entire demo to a Mantl cluster can be found at
* MyHero Demo - [hpreston/myhero_demo](https://github.com/hpreston/myhero_demo)

The application was designed to provide a simple demo for Cisco Mantl.  It is written as a simple Python Flask application and deployed as a docker container.

Other services are:
* Data - [hpreston/myhero_data](https://github.com/hpreston/myhero_data)
* App - [hpreston/myhero_app](https://github.com/hpreston/myhero_app)
* Web - [hpreston/myhero_web](https://github.com/hpreston/myhero_web)
* Ernst - [hpreston/myhero_ernst](https://github.com/hpreston/myhero_ernst)
  * Optional Service used along with an MQTT server when App is in "queue" mode
* Spark Bot - [hpreston/myhero_spark](https://github.com/hpreston/myhero_spark)
  * Optional Service that allows voting through IM/Chat with a Cisco Spark Bot
* Tropo App - [hpreston/myhero_tropo](https://github.com/hpreston/myhero_tropo)
  * Optional Service that allows voting through TXT/SMS messaging


The docker containers are available at
* Data - [hpreston/myhero_data](https://hub.docker.com/r/hpreston/myhero_data)
* App - [hpreston/myhero_app](https://hub.docker.com/r/hpreston/myhero_app)
* Web - [hpreston/myhero_web](https://hub.docker.com/r/hpreston/myhero_web)
* Ernst - [hpreston/myhero_ernst](https://hub.docker.com/r/hpreston/myhero_ernst)
  * Optional Service used along with an MQTT server when App is in "queue" mode
* Spark Bot - [hpreston/myhero_spark](https://hub.docker.com/r/hpreston/myhero_spark)
  * Optional Service that allows voting through IM/Chat with a Cisco Spark Bot
* Tropo App - [hpreston/myhero_tropo](https://hub.docker.com/r/hpreston/myhero_tropo)
  * Optional Service that allows voting through TXT/SMS messaging

## Environmental Requirement
This service requires an MQTT server or broker to be available that can be subscribed, where votes will be published by the APP service.  The larger [MyHero Demo](https://github.com/hpreston/myhero_demo) application leverages [Mosca](https://hub.docker.com/r/matteocollina/mosca/) as a MQTT server for this purpose, though any MQTT server or broker should work.

The Vagrant environment for local development of this service deploys a Mosca container along with the ernst service itself and leverages it for local development work.

 **NOT DONE YET**

## Basic Application Details

Required

* flask
* ArgumentParser
* requests
* paho-mqtt
* dnspython

# Environment Installation

    pip install -r requirements.txt

# Basic Usage

In order to run, the service needs 3 pieces of information to be provided:
* Data Server Address
* Data Server Authentication Key to Use
* MQTT Server IP and Port
  * This can be determined in 2 different ways
    * Explicitly Set
    * Dynamically learned by doing an DNS Lookup

These details can be provided in one of three ways.
* As a command line argument
  - `python myhero_ernst/myhero_ernst.py --dataserver "http://myhero-data.server.com" --datakey "DATA AUTH KEY" --appsecret "APP AUTH KEY" --mqtthost "192.168.1.10" --mqttport "1883" --mqttserver "mqtt.service.consul" `
* As environment variables
  - `export myhero_data_server="http://myhero-data.server.com"`
  - `export myhero_data_key="DATA AUTH KEY"`
  - `export myhero_mqtt_host=192.168.1.10`
  - `export myhero_mqtt_port=1883`
  - `export myhero_mqtt_server=mqtt.service.consul`
  - `python myhero_ernst/myhero_ernst.py`
* As raw input when the application is run
  - `python myhero_ernst/myhero_ernst.py`
  - `What is the data server address? http://myhero-data.server.com`
  - `Data Server Key: DATA AUTH KEY`
  - `App Server Key: APP AUTH KEY`

A command line argument overrides an environment variable, and raw input is only used if neither of the other two options provide needed details.

**For determining the MQTT Server IP and Port, explicitly setting them through Command Line Arguements or through ENV variables will be preferred over a DNS lookup**

# Alternate and Advanced Configurations

## Finding Data Server Details with SRV Lookup

If in your deployment, the myhero_data microservice is deployed in a way that the data server address (ie IP and Port) are dynamic, there is support for querying an SRV record to determine the details.

An example of this type of setup would be deploying MyHero to a Mantl.io cluster where Consul.io is used for service discovery.  Rather than hard code in the address of the data server, you would query Consul for the address infromation.

To use this method, you will provide a different argument or environment variable to the program.

* As a command line argument
  - `python myhero_ernst/myhero_ernst.py --datasrv "data-myhero.service.consul" --datakey "DATA AUTH KEY" --appsecret "APP AUTH KEY" --mqtthost "192.168.1.10" --mqttport "1883" --mqttserver "mqtt.service.consul" `
* As environment variables
  - `export myhero_data_srv"data-myhero.service.consul"`
  - `export myhero_data_key="DATA AUTH KEY"`
  - `export myhero_mqtt_host=192.168.1.10`
  - `export myhero_mqtt_port=1883`
  - `export myhero_mqtt_server=mqtt.service.consul`
  - `python myhero_ernst/myhero_ernst.py`


# Accessing

Initial and Basic APIs.
These are v1 APIs that require no authentication and will eventually be removed
* Basic List of Hero Choices
  * `curl http://localhost:5000/hero_list`
* Current results calculations
  * `curl http://localhost:5000/results`
* Place a vote for an option
  * `curl http://localhost:5000/vote/<HERO>`

New v2 APIs
These newer APIs require authentication as well as support more features
* Get the current list of options for voting
  * `curl -X GET -H "key: APP AUTH KEY" http://localhost:5000/options`
* Add a new option to the list
  * `curl -X PUT -H "key: APP AUTH KEY" http://localhost:5000/options -d '{"option":"Deadpool"}'`
* Replace the entire options list
  * `curl-X POST -H "key: APP AUTH KEY" http://localhost:5000/options -d @sample_post.json`
  * Data should be of same format as a GET request
* Delete a single option from the list
  * `curl -X DELETE -H "key: APP AUTH KEY" http://localhost:5000/options/Deadpool`
* Place a Vote for an option
  * `curl -X POST -H "key: APP AUTH KEY" http://localhost:5000/vote/Deadpool`
* Get current results
  * `curl -X GET -H "key: APP AUTH KEY" http://localhost:5000/results`

# Local Development with Vagrant

I've included the configuration files needed to do local development with Vagrant in the repo.  Vagrant will still use Docker for local development and is configured to spin up a CentOS7 host VM for running the container.

To start local development run:
* `vagrant up`
  - You may need to run this twice.  The first time to start the docker host, and the second to start the container.
* Now you can interact with the API or interface at localhost:15001 (configured in Vagrantfile and Vagrantfile.host)
  - example:  from your local machine `curl -H "key: DevApp" http://localhost:15001/options`
  - Environment Variables are configured in Vagrantfile for development

Each of the services in the application (i.e. myhero_web, myhero_app, and myhero_data) include Vagrant support to allow working locally on all three simultaneously.
