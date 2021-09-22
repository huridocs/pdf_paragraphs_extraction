## Get PDF paragraphs

This service uses machine learning to segment a PDF in paragraphs.

### Dependencies

* Docker [install] (https://runnable.com/docker/getting-started/)
* Docker-compose [install] (https://docs.docker.com/compose/install/)
    * Note: On mac Docker-compose is installed with Docker


### How to use it

Start service:

`docker-compose up`

Get paragraphs from a PDF:

`curl -X GET -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5051`

To stop the server:

`docker-compose down`

### How to use it asynchronously

<b>Configure the redis server</b>

If the configuration is not changed, a dockerized redis server will be used.

To use a different redis server, create a file `docker_volume/redis_server.yml` with the following content:

    host: [shost_ip]
    port: [port_number]

<b>Start the service</b>

    docker-compose up

<b>Add asynchronous extraction task</b>

To add start a segmentation task, a message should be sent to a queue

python
  queue = RedisSMQ(host=[redis host], port=[redis port], qname='segmentation_tasks', quiet=True)
  message = queue.sendMessage('{"tenant": "tenant_name", "task": "pdf_name.pdf"}').exceptions(False).execute()

Get redis message when extraction is done:

python
  queue = RedisSMQ(host=[redis host], port=[redis port], qname='segmentation_results', quiet=True)
  message = queue.receiveMessage().exceptions(False).execute()

js
  const rsmq = new RedisSMQ( {host: [redis host], port: [redis port], ns: "rsmq"} );
  
  rsmq.receiveMessage({ qname: "segmentation_results" }, (err, resp) => {
      if (resp.id) {
          console.log("received message:", resp.message);
      } else {
          console.log("no available message in queue..");
      }
  });

<b>Get paragraphs</b>

  curl -X GET localhost/get_paragraphs/[tenant_name]/[pdf_name]:5051

<b>Stop the service</b>

  docker-compose down

### Logs

The service logs are stored in the file `docker_volume/service.log`

To use a graylog server, create a file `docker_volume/graylog.yml` with the following content:

`graylog_ip: [ip]`

### Set up environment for development

It works with Python 3.9

    pip3 install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
### Execute tests

    python -m unittest