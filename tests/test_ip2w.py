import pytest
import requests
import json


service = 'http://localhost/ip2w/'


@pytest.mark.parametrize("test_input", [("176.14.221.123", "Moscow"), ("5.18.102.113", "Saint Petersburg")])
def test_correct_ip(test_input):
    ip, city = test_input
    resp = requests.get(service+ip)
    resp = json.loads(resp.content)
    assert resp['city'] == city


@pytest.mark.parametrize("test_input", ["127.0.0.1", "0.0.0.0"])
def test_incorrect_ip(test_input):
    resp = requests.get(service+test_input)
    assert resp.status_code == 400
