from redis import exceptions
from rsmq import RedisSMQ

REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"


def delete_queues():
    try:
        queue = RedisSMQ(
            host=REDIS_HOST,
            port=REDIS_PORT,
            qname="segmentation_tasks",
            quiet=False,
        )

        queue.deleteQueue().exceptions(False).execute()
        queue.createQueue().exceptions(False).execute()

        queue = RedisSMQ(
            host=REDIS_HOST,
            port=REDIS_PORT,
            qname="segmentation_results",
            quiet=False,
        )

        queue.deleteQueue().exceptions(False).execute()
        queue.createQueue().exceptions(False).execute()

        print("Queues properly deleted")

    except exceptions.ConnectionError:
        print("No redis connection")


if __name__ == "__main__":
    delete_queues()
