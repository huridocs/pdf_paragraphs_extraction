from redis import exceptions
from rsmq import RedisSMQ

REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"


def print_queue_messages():
    queue = RedisSMQ(
        host=REDIS_HOST,
        port=REDIS_PORT,
        qname="segmentation_tasks",
        quiet=False,
    )

    try:
        attributes = queue.getQueueAttributes().exec_command()
        print("Messages in queue ", attributes["msgs"])
        print("Messages executed ", attributes["totalrecv"])
    except exceptions.ConnectionError:
        print("No redis connection")


if __name__ == "__main__":
    print_queue_messages()
