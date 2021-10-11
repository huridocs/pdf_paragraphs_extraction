import os
import socket

import yaml


def create_configuration():
    config_dict = dict()
    if os.path.exists('config.yml'):
        with open("config.yml", 'r') as f:
            config_dict = yaml.safe_load(f)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    config_dict['service_host'] = s.getsockname()[0]
    s.close()

    with open("docker-compose.yml", 'r') as f:
        config_dict['service_port'] = yaml.safe_load(f)['services']['server']['ports'][0].split(':')[0]

    write_configuration(config_dict)


def write_configuration(config_dict):
    with open('config.yml', 'w') as config_file:
        for config_key, config_value in config_dict.items():
            config_file.write(f'{config_key}: {config_value}\n')


if __name__ == '__main__':
    create_configuration()
