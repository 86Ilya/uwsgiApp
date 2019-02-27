#!/usr/bin/env python2
import logging
import requests
import json
import os
import re

DEFAULT_CONFIG = {
    'logging_level': logging.INFO,
    'logfile': '/var/log/otus/otus_ip2w.log',
    'log_format': {'format': '[%(asctime)s] %(levelname).1s %(message)s', 'datefmt': '%Y.%m.%d %H:%M:%S'},
}
cfg_path = '/usr/local/etc/ip2w.conf'
ipinfo_endpoint = "http://ipinfo.io/{}/geo?token={}"
weather_endpoint = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
kelvin = -272.15

status_ok = '200 OK'
status_bad = '400 Bad Request'
response_headers_bad = [
    ('Content-Type', 'text/plain'),
    ('Content-Length', 0)
]
pattern = re.compile(r'ip2w\/(?P<addr>\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3})')


def application(environ, start_response):
    try:
        config = update_config(cfg_path, DEFAULT_CONFIG)
        ipinfo_token = config['ipinfo_token']
        logging.basicConfig(logfile=config['logfile'], level=config['logging_level'],
                            format=config['log_format']['format'],
                            datefmt=config['log_format']['datefmt'])
        ip = pattern.search(environ["REQUEST_URI"])
        if ip:
            ip = ip.groupdict().get('addr')
        else:
            raise ValueError("Request doesn't have a valid IP address")

        logging.info("Getting info about ip: {}".format(ip))
        ipaddr_resp = requests.get(ipinfo_endpoint.format(ip, ipinfo_token))
        logging.debug("Info about IP: {}".format(ipaddr_resp))
        ipaddr_resp = json.loads(ipaddr_resp.content)
        lat, lon = ipaddr_resp["loc"].split(',')
    except Exception as error:
        logging.error("We have error while trying to get info about IP: {}".format(error))
        start_response(status_bad, response_headers_bad)
        return [None]

    try:
        logging.info("Getting info about weather.")
        weather_token = config['weather_token']
        weather_resp = requests.get(weather_endpoint.format(lat, lon, weather_token))
        logging.debug("Weather service response: {}".format(weather_resp))
    except Exception as error:
        logging.error("We have error while trying to get info about weather: {}".format(error))
        start_response(status_bad, response_headers_bad)
        return [None]
    weather = json.loads(weather_resp.content)
    response_dict = dict()

    response_dict["city"] = weather['name']
    response_dict["temp"] = "{:.2f}".format(weather['main']['temp'] + kelvin)
    response_dict["conditions"] = weather['weather'][0]['main']
    response_body = json.dumps(response_dict)
    response_body = response_body.encode()

    # So the content-length is the sum of all string's lengths
    content_length = len(response_body)

    response_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(content_length))
    ]
    start_response(status_ok, response_headers)
    return [response_body]


def update_config(cfg_path, default_config):
    config = default_config.copy()

    if os.path.exists(cfg_path):
        with open(cfg_path, 'r') as cfg_file:
            try:
                config.update(json.loads(cfg_file.read()))
            except Exception as error:
                print("Error while trying read config file of application: {}".format(error))
                raise
    return config
