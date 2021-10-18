import logging
import os

import graypy
import yaml


def get_logger(logger_name):
    logger = logging.getLogger('graylog')
    logger.setLevel(logging.INFO)

    if not os.path.exists('config.yml') or not yaml.safe_load(open("config.yml", 'r')):
        logger.addHandler(logging.FileHandler(f'./docker_volume/{logger_name}.log'))
        return logger

    if 'graylog_ip' not in yaml.safe_load(open("config.yml", 'r')):
        logger.addHandler(logging.FileHandler(f'./docker_volume/{logger_name}.log'))
        return logger

    graylog_ip = yaml.safe_load(open("config.yml", 'r'))['graylog_ip']
    handler = graypy.GELFUDPHandler(graylog_ip, 12201, localname="get_pdf_paragraphs")
    logger.addHandler(handler)
    return logger
