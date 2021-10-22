<h3 align="center">Extract PDF paragraphs</h3>
<p align="center">A Docker-powered service for extracting paragraphs from PDFs</p>

---

This service provides one endpoint to get paragraphs from PDFs. The paragraphs
contain the page number, the position in the page, the size, and the text. Furthermore, there is 
an option to get an asynchronous flow using message queues on redis.

## Quick Start
Start the service:

    docker-compose up

Get the paragraphs from a PDF:

    curl -X GET -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5051

To stop the server:

    docker-compose down

## Contents
- [Quick Start](#quick-start)
- [Dependencies](#dependencies)
- [Requirements](#requirements)
- [How to use it asynchronously](#how-to-use-it-asynchronously)
- [Get service logs](#get-service-logs)
- [Set up environment for development](#set-up-environment-for-development)
- [Execute tests](#execute-tests)
- [Troubleshooting](#troubleshooting)


## Dependencies
* Docker [install] (https://runnable.com/docker/getting-started/)
* Docker-compose [install] (https://docs.docker.com/compose/install/)
    * Note: On mac Docker-compose is installed with Docker
    

## Requirements

* 2Gb RAM memory
* Single core
  
## How to use it asynchronously

A redis server is needed to use the service asynchronously. For that matter, it can be used the 
docker-compose file `docker-compose-service-with-redis.yml` that has a built-in 
redis server.

Containers with `docker-compose up`

![Alt logo](readme_pictures/docker_compose_up.png?raw=true "docker-compose up")

Containers with `docker-compose -f docker-compose-service-with-redis.yml up`

![Alt logo](readme_pictures/docker_compose_redis.png?raw=true "docker-compose -f docker-compose-service-with-redis.yml up")


<b>Configuration file</b>

A configuration file could be provided to set the redis server parameters
and the `extract pdf paragraphs` server hosts and ports. If a configuration is not provided,
the defaults values uses the redis from the 'docker-compose-service-with-redis.yml' 
file.

File name: `config.yml`

Parameters:

    service_host: [shost_ip]
    service_port: [port_number]
    redis_host: [redis_host]
    redis_port: [redis_port]

<b>Asynchronous flow</b>

1. Send PDF to extract

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5051/async_extraction/[tenant_name]

![Alt logo](readme_pictures/send_materials.png?raw=true "Send PDF to extract")


2. Add extraction task

To add an extraction task, a message should be sent to a queue.

Python code:

    queue = RedisSMQ(host=[redis host], port=[redis port], qname='segmentation_tasks', quiet=True)
    message_json = '{"tenant": "tenant_name", "task": "segmentation", "params": {"filename": "pdf_file_name.pdf"}}'
    message = queue.sendMessage(message_json).exceptions(False).execute()


![Alt logo](readme_pictures/extraction.png?raw=true "Add extraction task")

3. Get paragraphs

When the segmentation task is done, a message is placed in the results queue:

    queue = RedisSMQ(host=[redis host], port=[redis port], qname='segmentation_results', quiet=True)
    results_message = queue.receiveMessage().exceptions(False).execute()

    # The message.message contains the following information:
    # {"tenant": "tenant_name", 
    # "task": "pdf_name.pdf", 
    # "success": true, 
    # "error_message": "", 
    # "data_url": "http://localhost:5051/get_paragraphs/[tenant_name]/[pdf_name]"
    # "file_url": "http://localhost:5051/get_xml/[tenant_name]/[pdf_name]"
    # }


    curl -X GET http://localhost:5051/get_paragraphs/[tenant_name]/[pdf_name]
    curl -X GET http://localhost:5051/get_xml/[tenant_name]/[pdf_name]

or in python

    requests.get(results_message.data_url)
    requests.get(results_message.file_url)

![Alt logo](readme_pictures/get_paragraphs.png?raw=true "Get paragraphs")

## Get service logs

The service logs are stored by default in the files `docker_volume/service.log` and `docker_volume/redis_tasks.log`

To use a graylog server, create a file `config.yml` with the following content:

    graylog_ip: [ip]

## Set up environment for development

It works with Python 3.9 [install] (https://runnable.com/docker/getting-started/)

    pip3 install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Execute tests

    python -m unittest

## Troubleshooting

Issue: Permission error starting the docker containers
Cause: Due to docker creating files with the root user some permission errors can occur starting the docker containers.
Solution: There are two solutions. 

First solution is running docker with sudo

    sudo docker-compose up 

Second solution is setting up a development environment and running 

    sudo python clean_files.py
    docker-compose up 
