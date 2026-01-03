from http import HTTPStatus

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_read_root_should_return_hello_world():
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}
