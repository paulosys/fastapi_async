from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from jwt import decode, encode

from fastapi_async.security import create_access_token


def test_jwt(settings):
    data = {'sub': 'testuser'}

    token = create_access_token(data)

    decoded = decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert decoded['sub'] == 'testuser'


def test_jwt_invalid_token(client):
    invalid_token = 'invalid.token.value'

    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {invalid_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_expired_token(client, settings):
    expired_payload = {
        'sub': 'testuser',
        'exp': datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    expired_token = encode(
        expired_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {expired_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Token has expired'}
