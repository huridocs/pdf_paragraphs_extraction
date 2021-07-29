# Get PDF paragraphs

This service uses machine learning to segment a PDF in paragraphs.

# How to use it

Start service:

  `docker-compose up`

Get paragraphs from a PDF:

   `curl -i -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5010/segment`

To stop the server:

  `docker-compose down`


## Dependencies
 * Docker [install] (https://runnable.com/docker/getting-started/)
 * Docker-compose [install] (https://docs.docker.com/compose/install/)
    * Note: On mac Docker-compose is installed with Docker


## Configuring external graylog server 

Set graylog ip in the ./config.py file:

   `GRAYLOG_IP = "GRAYLOG IP"`


## Check service graylog's logs in local

Execute the service in dev mode

   `docker-compose -f docker-compose.dev.yml up`

For the logging solution graylog is used.

To check the logs in local go to the url:
`localhost:9000`

User: admin
Password: admin

And setup the input `GELF UDP Global` in settings/input