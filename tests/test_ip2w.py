# -*- coding: utf-8 -*-
import pytest
import requests
import json

host = 'http://localhost/'
service = 'ip2w/'
endpoint = host + service


@pytest.mark.parametrize("test_input", [("176.14.221.123", "Moscow"), ("5.18.102.113", "Saint Petersburg")])
def test_processing_when_request_is_correct(test_input):
    ip, city = test_input
    resp = requests.get(endpoint + ip)
    resp = json.loads(resp.content)
    assert resp['city'] == city


@pytest.mark.parametrize("test_input", ["127.0.0.1", "0.0.0.0"])
def test_processing_when_request_is_incorrect(test_input):
    resp = requests.get(endpoint + test_input)
    assert resp.status_code == 400
