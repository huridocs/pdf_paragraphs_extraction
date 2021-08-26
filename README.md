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
server_ip: [server_ip]
server_port: [port_number]
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

### Configuring external graylog server

Set graylog ip in the ./graylog.yml file:

`graylog_ip:[ip]`

### Check service graylog's logs in local

Set graylog ip in the ./graylog.yml file:

`graylog_ip:graylog`

Execute the service in dev mode

`docker-compose -f docker-compose.dev.yml up`

For the logging solution graylog is used.

To check the logs in local go to the url:
`localhost:9000`

User: admin Password: admin

And setup the input `GELF UDP Global` in settings/input