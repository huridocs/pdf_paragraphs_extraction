import json
import os

from rsmq import RedisSMQ
from rsmq.consumer import RedisSMQConsumer

# host = 'redis_paragraphs'
from data.ExtractionMessage import ExtractionMessage

host = '127.0.0.1'

if __name__ == '__main__':
    queue = RedisSMQ(host=host, qname="paragraphs_extraction")
    queue.deleteQueue().exceptions(False).execute()
    queue.createQueue().exceptions(False).execute()
    extraction_message = ExtractionMessage(tenant='a', pdf_file_name='b', success=True)
    queue.sendMessage(delay=0).message(extraction_message.dict()).execute()
    message = queue.receiveMessage().exceptions(False).execute()
    print(message['message'])

    extraction_message = ExtractionMessage(**json.loads(message['message']))
    print(extraction_message.tenant)
