import pytest
import requests

import controller.proxy as proxy
import server
try:
    import common.exceptions as exceptions
    import common.model as model
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')


def test_server_init():
    app = server


@pytest.mark.server(url='/', response={'components': [], 'systems': [], 'results': [], 'comments': []}, method='GET')
def test_get_metric():
    response = requests.get('http://localhost:5000/')
    assert response.status_code == 200
    assert response.json() == {'components': [], 'systems': [], 'results': [], 'comments': []}
