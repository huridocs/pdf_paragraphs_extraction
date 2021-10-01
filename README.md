## Get PDF paragraphs

This service uses machine learning to segment a PDF in paragraphs.

### Dependencies

* Docker [install] (https://runnable.com/docker/getting-started/)
* Docker-compose [install] (https://docs.docker.com/compose/install/)
    * Note: On mac Docker-compose is installed with Docker


### How to use it

Start service:

    docker-compose up

Get paragraphs from a PDF:

    curl -X GET -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5051

To stop the server:

    docker-compose down

### How to use it asynchronously

<b>Configure the redis server</b>

If the configuration is not changed, a dockerized redis server will be used in port <b>6479</b>

To use a different redis server, create a file `docker_volume/redis_server.yml` with the following content:

    host: [shost_ip]
    port: [port_number]

<b>Start the service</b>

    docker-compose up

<b>Send PDF to segment asynchronously</b>

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5051/async_extraction/[tenant_name]

<b>Add asynchronous extraction task</b>

To add a segmentation task, a message should be sent to a queue

    queue = RedisSMQ(host=[redis host], port=[redis port], qname='segmentation_tasks', quiet=True)
    message = queue.sendMessage('{"tenant": "tenant_name", "task": "pdf_name.pdf"}').exceptions(False).execute()

When the segmentation task is done, a message is placed in the results queue:

    queue = RedisSMQ(host=[redis host], port=[redis port], qname='segmentation_results', quiet=True)
    message = queue.receiveMessage().exceptions(False).execute()

    # The message.message contains the following information:
    # {"tenant": "tenant_name", "task": "pdf_name.pdf", "success": true, "error_message": ""}

<b>Get paragraphs</b>

    curl -X GET localhost:5051/get_paragraphs/[tenant_name]/[pdf_name]

<b>Stop the service</b>

    docker-compose down

### Logs

The service logs are stored in the file `docker_volume/service.log`

To use a graylog server, create a file `docker_volume/graylog.yml` with the following content:

    graylog_ip: [ip]

### Set up environment for development

It works with Python 3.9 [install] (https://runnable.com/docker/getting-started/)

    pip3 install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
### Execute tests

    python -m unittest