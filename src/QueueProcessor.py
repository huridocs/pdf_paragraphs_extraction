import os
from time import sleep

import pymongo
import redis
from pydantic import ValidationError
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ, cmd
from sentry_sdk.integrations.redis import RedisIntegration
import sentry_sdk

from ServiceConfig import ServiceConfig
from data.ExtractionMessage import ExtractionMessage
from data.Task import Task
from extract_pdf_paragraphs.extract_paragraphs import extract_paragraphs


class QueueProcessor:
    def __init__(self):
        self.config = ServiceConfig()
        self.logger = self.config.get_logger("redis_tasks")

        client = pymongo.MongoClient(f"mongodb://{self.config.mongo_host}:{self.config.mongo_port}")
        self.pdf_paragraph_db = client["pdf_paragraph"]

        self.results_queue = RedisSMQ(
            host=self.config.redis_host,
            port=self.config.redis_port,
            qname=self.config.results_queue_name,
        )
        self.extractions_tasks_queue = RedisSMQ(
            host=self.config.redis_host,
            port=self.config.redis_port,
            qname=self.config.tasks_queue_name,
        )

    def process(self, id, message, rc, ts):
        try:
            task = Task(**message)
        except ValidationError:
            self.logger.error(f"Not a valid Redis message: {message}")
            return True

        self.logger.info(f"Processing Redis message: {message}")

        try:
            extraction_data = extract_paragraphs(task)

            if not extraction_data:
                extraction_message = ExtractionMessage(
                    tenant=task.tenant,
                    task=task.task,
                    params=task.params,
                    success=False,
                    error_message="Error getting the xml from the pdf",
                )

                self.results_queue.sendMessage().message(extraction_message.dict()).execute()
                self.logger.error(extraction_message.json())
                return True

            results_url = f"{self.config.service_url}/get_paragraphs/{task.tenant}/{task.params.filename}"
            file_results_url = f"{self.config.service_url}/get_xml/{task.tenant}/{task.params.filename}"
            extraction_message = ExtractionMessage(
                tenant=extraction_data.tenant,
                task=task.task,
                params=task.params,
                success=True,
                data_url=results_url,
                file_url=file_results_url,
            )

            self.pdf_paragraph_db.paragraphs.insert_one(extraction_data.dict())
            self.logger.info(f"Results Redis message: {extraction_message}")
            self.results_queue.sendMessage(delay=3).message(extraction_message.dict()).execute()
            return True
        except Exception:
            self.logger.error("error extracting the paragraphs", exc_info=1)
            return True

    def subscribe_to_extractions_tasks_queue(self):
        while True:
            try:
                self.extractions_tasks_queue.getQueueAttributes().exec_command()
                self.results_queue.getQueueAttributes().exec_command()

                self.logger.info(f"Connecting to redis: {self.config.redis_host}:{self.config.redis_port}")

                redis_smq_consumer = RedisSMQConsumer(
                    qname=self.config.tasks_queue_name,
                    processor=self.process,
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                )
                redis_smq_consumer.run()
            except redis.exceptions.ConnectionError:
                self.logger.error(f"Error connecting to redis: {self.config.redis_host}:{self.config.redis_port}")
                sleep(20)
            except cmd.exceptions.QueueDoesNotExist:
                self.logger.info("Creating queues")
                self.extractions_tasks_queue.createQueue().vt(120).exceptions(False).execute()
                self.results_queue.createQueue().exceptions(False).execute()
                self.logger.info("Queues have been created")


if __name__ == "__main__":
    try:
        sentry_sdk.init(
            os.environ.get("SENTRY_DSN"),
            traces_sample_rate=0.1,
            environment=os.environ.get("ENVIRONMENT", "development"),
            integrations=[RedisIntegration()],
        )
    except Exception:
        pass

    redis_tasks_processor = QueueProcessor()
    redis_tasks_processor.subscribe_to_extractions_tasks_queue()
