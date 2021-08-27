## Get PDF paragraphs

This service uses machine learning to segment a PDF in paragraphs.

### How to use it

Start service:

`docker-compose up`

Get paragraphs from a PDF:

`curl -X GET -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5051`

To stop the server:

`docker-compose down`

### How to use it asynchronously

Start service:

`docker-compose up`

Configure redis server:

- Create file `redis_server.yml` inside the project root with the content

```
host: [shost_ip]
port: [port_number]
```

Add asynchronous extraction task:

`curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost/async_extraction/[tenant_name]:5051`

Get redis message when extraction is done:

python
```
queue = RedisSMQ(host=[redis host], port=[redis port], qname='paragraphs_extraction', quiet=True)
message = queue.receiveMessage().exceptions(False).execute()
```

js
```
const rsmq = new RedisSMQ( {host: [redis host], port: [redis port], ns: "rsmq"} );

rsmq.receiveMessage({ qname: "paragraphs_extraction" }, (err, resp) => {
    if (resp.id) {
        console.log("received message:", resp.message);
    } else {
        console.log("no available message in queue..");
    }
});
```

Get paragraphs:

`curl -X GET localhost/get_paragraphs/[tenant_name]/[pdf_name]:5051`

To stop the server:

`docker-compose down`

### Dependencies

* Docker [install] (https://runnable.com/docker/getting-started/)
* Docker-compose [install] (https://docs.docker.com/compose/install/)
    * Note: On mac Docker-compose is installed with Docker

### Logs

The service logs are stored in the file `service.log`

To use a graylog server, create a file `./graylog.yml` in the project root folder with the following content:

`graylog_ip: [ip]`