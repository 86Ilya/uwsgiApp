#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
import requests
import json
import os
import re

DEFAULT_CONFIG = {
    'logging_level': logging.INFO,
    'logfile': None,
    'log_format': {'format': '[%(asctime)s] %(levelname).1s %(message)s', 'datefmt': '%Y.%m.%d %H:%M:%S'},
    'TIMEOUT': 15,
    'RECONNECT_ATTEMPTS': 5
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
pattern = re.compile(r'^\/ip2w\/(?P<addr>\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3})')


class WeatherAppException(ValueError):
    pass


def get(arguments, reconnect_attempts, timeout):
    """
    Обёртка над requests.get с добавлением попыток реконнекта и таймаутом
    :param arguments:
    :param int reconnect_attempts:
    :param int timeout:
    :return
    """
    for _ in range(reconnect_attempts):
        result = requests.get(arguments, timeout=timeout)
        if result:
            return result
    raise WeatherAppException("Reconnect attempts exceeded")


def get_coordinates_by_ip(environ, config):
    """
    Функция определяет координаты по  IP адресу
    :param dict environ:
    :param dict config:
    :return tuple (latitude, longitude):
    """
    try:
        ip = pattern.match(environ["REQUEST_URI"])
        if ip:
            ip = ip.groupdict().get('addr')
        else:
            raise WeatherAppException("Request doesn't have a valid IP address")

        ipinfo_token = config['ipinfo_token']
        logging.info("Getting info about ip: {}".format(ip))
        ipaddr_resp = get(ipinfo_endpoint.format(ip, ipinfo_token),
                          config['RECONNECT_ATTEMPTS'], config['TIMEOUT'])
        logging.debug("Info about IP: {}".format(ipaddr_resp))
        ipaddr_resp = json.loads(ipaddr_resp.content)
        lat, lon = ipaddr_resp["loc"].split(',')
        return lat, lon
    except Exception as error:
        logging.error("We have error while trying to get info about IP: {}".format(error))
        raise WeatherAppException(error)


def get_weather_info_by_coordinates(coord, config):
    """
    Функция определяет погоду по координатам
    :param tuple coord:
    :param dict config:
    :return dict: Словарь с ключами city, temp, conditions
    """
    try:
        lat, lon = coord
        logging.info("Getting info about weather.")
        weather_token = config['weather_token']
        weather_resp = get(weather_endpoint.format(lat, lon, weather_token),
                           config['RECONNECT_ATTEMPTS'], config['TIMEOUT'])
        logging.debug("Weather service response: {}".format(weather_resp))
    except Exception as error:
        logging.error("We have error while trying to get info about weather: {}".format(error))
        raise WeatherAppException(error)

    weather = json.loads(weather_resp.content)
    response_dict = dict()

    try:
        response_dict["city"] = weather['name']
        response_dict["temp"] = "{:.2f}".format(weather['main']['temp'] + kelvin)
        response_dict["conditions"] = weather['weather'][0]['main']
        return response_dict

    except Exception as error:
        logging.error("We have error while trying to parse weather response: {}".format(error))
        raise WeatherAppException(error)


def application(environ, start_response):
    """
    Приложение определяющее погоду по IP адресу
    :param dict environ: Переменные окружения в которых находится вся информация по запросу.
    :param method start_response: Метод обработки ответа
    :return:
    """
    try:
        config = update_config(cfg_path, DEFAULT_CONFIG)
        logging.basicConfig(filename=config['logfile'], level=config['logging_level'],
                            format=config['log_format']['format'],
                            datefmt=config['log_format']['datefmt'])

        coord = get_coordinates_by_ip(environ, config)
        weather = get_weather_info_by_coordinates(coord, config)
        response_body = json.dumps(weather)
        response_body = response_body.encode()
        # So the content-length is the sum of all string's lengths
        content_length = len(response_body)

        response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(content_length))
        ]
        start_response(status_ok, response_headers)
        return [response_body]

    except WeatherAppException:
        start_response(status_bad, response_headers_bad)
        return [None]


def update_config(cfg_path, default_config):
    """
    Функция обновляет конфиг по умолчанию данными из файла конфига и возвращает новый конфиг.
    :param string cfg_path: Путь к файлу конфига
    :param dict default_config: Словарь конфига по умолчанию
    :return dict:
    """
    config = default_config.copy()

    if os.path.exists(cfg_path):
        with open(cfg_path, 'r') as cfg_file:
            try:
                config.update(json.loads(cfg_file.read()))
            except Exception as error:
                print("Error while trying read config file of application: {}".format(error))
                raise
    return config
