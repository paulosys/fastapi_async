from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from jwt import decode, encode

from security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt():
    data = {'sub': 'testuser'}

    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded['sub'] == 'testuser'


def test_jwt_invalid_token(client):
    invalid_token = "invalid.token.value"

    response = client.get("/users", headers={"Authorization": f"Bearer {invalid_token}"})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "detail": "Could not validate credentials"
    }


def test_jwt_expired_token(client):

    expired_payload = {
        "sub": "testuser",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)  # Expired 1 minute ago
    }
    expired_token = encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get("/users", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "detail": "Token has expired"
    }
