from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_get_token_should_return_access_token(client, user):
    payload = {
        'username': user.username,
        'password': user.clean_password,
    }

    response = client.post('/auth/token', data=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert 'access_token' in response_data
    assert response_data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_get_token_with_invalid_credentials_should_return_401(client):
    payload = {
        'username': 'nonexistentuser',
        'password': 'wrongpassword',
    }

    response = client.post('/auth/token', data=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    response_data = response.json()
    assert response_data['detail'] == 'Incorrect username or password'


@pytest.mark.asyncio
async def test_get_token_with_wrong_password_should_return_401(client, user):
    payload = {
        'username': user.username,
        'password': 'wrongpassword',
    }

    response = client.post('/auth/token', data=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    response_data = response.json()
    assert response_data['detail'] == 'Incorrect username or password'
