import logging
import os

import graypy
import yaml


def get_graylog():
    graylog = logging.getLogger('graylog')
    graylog.setLevel(logging.INFO)

    if os.path.exists('graylog.yml'):
        graylog_ip = yaml.safe_load(open("graylog.yml", 'r'))['graylog_ip']
        handler = graypy.GELFUDPHandler(graylog_ip, 12201, localname="get_pdf_paragraphs")
        graylog.addHandler(handler)

    return graylog
