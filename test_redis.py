from rsmq import RedisSMQ
from rsmq.consumer import RedisSMQConsumer

host = 'redis_paragraphs'
# host = '127.0.0.1'


def processor(id, message, rc, ts):
    print(message)
    return True


if __name__ == '__main__':
    print('testing rediiiiiiiiiiiiis')
    queue = RedisSMQ(host=host, qname="paragraphs_extraction")
    queue.deleteQueue().exceptions(False).execute()
    queue.createQueue(delay=0).vt(20).execute()
    queue.sendMessage(delay=0).message({'message': 1}).execute()
    consumer = RedisSMQConsumer('paragraphs_extraction', processor, host=host)
    consumer.run()
