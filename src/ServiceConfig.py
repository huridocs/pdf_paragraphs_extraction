import logging
import os
from typing import Dict
from pathlib import Path

import graypy
import yaml

OPTIONS = [
    "redis_host",
    "redis_port",
    "service_host",
    "service_port",
    "mongo_host",
    "mongo_port",
    "graylog_ip",
]
SERVICE_NAME = "segmentation"

APP_PATH = Path(__file__).parent.absolute()


class ServiceConfig:
    def __init__(self):
        self.config_from_yml: Dict[str, any] = dict()

        self.docker_volume_path = f"{APP_PATH}/../docker_volume"
        self.create_docker_volume()

        self.tasks_queue_name = SERVICE_NAME + "_tasks"
        self.results_queue_name = SERVICE_NAME + "_results"

        self.config_path = "config.yml"
        self.read_configuration_from_yml()

        self.redis_host = self.get_parameter_from_yml("redis_host", "127.0.0.1")
        self.redis_port = self.get_parameter_from_yml("redis_port", 6379)

        self.service_host = self.get_parameter_from_yml("service_host", "localhost")
        self.service_port = self.get_parameter_from_yml("service_port", 5051)
        self.service_url = f"http://{self.service_host}:{self.service_port}"

        self.mongo_host = self.get_parameter_from_yml("mongo_host", "127.0.0.1")
        self.mongo_port = self.get_parameter_from_yml("mongo_port", 28017)

        self.graylog_ip = self.get_parameter_from_yml("graylog_ip", "")

    def get_parameter_from_yml(self, parameter_name: str, default: any):
        if parameter_name in self.config_from_yml:
            return self.config_from_yml[parameter_name]

        return default

    def read_configuration_from_yml(self):
        if not os.path.exists(self.config_path):
            return dict()

        with open(self.config_path, "r") as f:
            config_from_yml = yaml.safe_load(f)
            if config_from_yml:
                self.config_from_yml = config_from_yml

        return dict()

    def get_logger(self, logger_name):
        logger = logging.getLogger("graylog")
        logger.setLevel(logging.INFO)

        if self.graylog_ip:
            handler = graypy.GELFUDPHandler(
                self.config_from_yml["graylog_ip"],
                12201,
                localname="segmentation_server",
            )
        else:
            handler = logging.FileHandler(
                f"{self.docker_volume_path}/{logger_name}.log"
            )

        logger.addHandler(handler)
        return logger

    def write_configuration(self, config_dict: Dict[str, str]):
        config_to_write = dict()
        for config_key, config_value in config_dict.items():
            if not config_value and config_key not in self.config_from_yml:
                continue

            if not config_value and config_key in self.config_from_yml:
                config_to_write[config_key] = self.config_from_yml[config_key]
                continue

            config_to_write[config_key] = config_value

        if "graylog_ip" in self.config_from_yml:
            config_to_write["graylog_ip"] = self.config_from_yml["graylog_ip"]

        if len(config_to_write) == 0:
            return

        with open("config.yml", "w") as config_file:
            config_file.write(
                "\n".join([f"{k}: {v}" for k, v in config_to_write.items()])
            )

    def create_configuration(self):
        config_dict = dict()

        config_dict["redis_host"] = self.redis_host
        config_dict["redis_port"] = self.redis_port
        config_dict["service_host"] = self.service_host
        config_dict["service_port"] = self.service_port
        config_dict["mongo_host"] = self.mongo_host
        config_dict["mongo_port"] = self.mongo_port
        config_dict["graylog_ip"] = self.graylog_ip

        print(":::::::::: Actual configuration :::::::::::\n")
        for config_key in config_dict:
            print(f"{config_key}: {config_dict[config_key]}")

        user_input = None

        while user_input not in ("yes", "n", "y", "no", "N", "Y", ""):
            user_input = input("\nDo you want to change the configuration? [Y/n]\n")

        if user_input != "" and user_input[0].lower() == "n":
            return

        print("[Enter to DO NOT modify it]")
        for option in OPTIONS:
            configuration_input = input(f"{option}: [{config_dict[option]}] ")
            config_dict[option] = configuration_input

        self.write_configuration(config_dict)

    def create_docker_volume(self):
        if not os.path.exists(self.docker_volume_path):
            os.mkdir(self.docker_volume_path)


if __name__ == "__main__":
    config = ServiceConfig()
    config.create_configuration()
