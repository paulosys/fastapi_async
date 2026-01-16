from http import HTTPStatus

import pytest
from freezegun import freeze_time


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
    assert response_data['token_type'] == 'Bearer'


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


def test_token_expired_after_time(client, user):
    with freeze_time('2026-01-01 12:00:00'):
        payload = {
            'username': user.username,
            'password': user.clean_password,
        }
        response = client.post('/auth/token', data=payload)
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-01-01 13:01:00'):
        headers = {'Authorization': f'Bearer {token}'}

        response = client.put(
            f'/users/{user.id}',
            headers=headers,
            json={
                'username': 'wrong',
                'email': 'wrong@email.com',
                'password': 'wrongpassword',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        response_data = response.json()
        assert response_data['detail'] == 'Token has expired'


def test_invalid_token_error(client):
    invalid_token = 'thisis.aninvalid.token'
    headers = {'Authorization': f'Bearer {invalid_token}'}

    response = client.get('/users/', headers=headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    response_data = response.json()
    assert response_data['detail'] == 'Could not validate credentials'


def test_token_wrong_password(client, user):
    payload = {
        'username': user.username,
        'password': 'wrongpassword',
    }

    response = client.post('/auth/token', data=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    response_data = response.json()
    assert response_data['detail'] == 'Incorrect username or password'


def test_token_inexistent_user(client):
    payload = {
        'username': 'nonexistentuser',
        'password': 'somepassword',
    }

    response = client.post('/auth/token', data=payload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    response_data = response.json()
    assert response_data['detail'] == 'Incorrect username or password'


def test_refresh_token_should_return_new_access_token(client, token):
    headers = {'Authorization': f'Bearer {token}'}

    response = client.post('/auth/refresh-token', headers=headers)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert 'access_token' in response_data
    assert response_data['token_type'] == 'Bearer'


def test_refresh_token_expired_dont_refresh(client, user):
    with freeze_time('2026-01-01 12:00:00'):
        payload = {
            'username': user.username,
            'password': user.clean_password,
        }
        response = client.post('/auth/token', data=payload)
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-01-01 13:01:00'):
        headers = {'Authorization': f'Bearer {token}'}

        response = client.post('/auth/refresh-token', headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        response_data = response.json()
        assert response_data['detail'] == 'Token has expired'
