from http import HTTPStatus

import pytest

from fastapi_async.schemas import UserOutSchema


@pytest.mark.asyncio
async def test_create_user_should_return_created_user(client):
    payload = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'securepassword123',
    }
    response = client.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    assert response_data['username'] == payload['username']
    assert response_data['email'] == payload['email']
    assert 'id' in response_data


@pytest.mark.asyncio
async def test_create_user_with_existing_email_should_return_409(client, user):
    payload = {
        'username': 'newuser',
        'email': user.email,
        'password': 'anotherpassword123',
    }

    response = client.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CONFLICT
    response_data = response.json()['detail']
    assert response_data == 'User with this email or username already exists!'


@pytest.mark.asyncio
async def test_list_users_should_return_all_users(client, user, token):
    user_schema = UserOutSchema.model_validate(user).model_dump()

    response = client.get(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['users'] == [user_schema]


@pytest.mark.asyncio
async def test_update_user_should_return_updated_user(client, user, token):
    payload = {
        'username': 'updatableuser',
        'email': 'updatableuser@example.com',
        'password': 'securepassword123',
    }

    response = client.put(
        f'/users/{user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['username'] == payload['username']
    assert response_data['email'] == payload['email']
    assert response_data['id'] == user.id


@pytest.mark.asyncio
async def test_update_user_with_existing_email_should_return_409(
    client,
    user,
    another_user,
    token,
):
    payload = {
        'username': user.username,
        'email': another_user.email,
        'password': 'securepassword123',
    }

    response = client.put(
        f'/users/{user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    response_data = response.json()['detail']
    assert response_data == 'User with this email or username already exists!'


@pytest.mark.asyncio
async def test_update_other_user_should_return_403(
    client,
    another_user,
    token,
):
    payload = {
        'username': 'hackeruser',
        'email': 'hackeruser@example.com',
        'password': 'securepassword123',
    }

    response = client.put(
        f'/users/{another_user.id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    response_data = response.json()['detail']
    assert response_data == 'You do not have permission to update this user!'


@pytest.mark.asyncio
async def test_delete_user_should_return_no_content(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['message'] == 'User deleted successfully!'


@pytest.mark.asyncio
async def test_delete_other_user_should_return_403(
    client,
    another_user,
    token,
):
    response = client.delete(
        f'/users/{another_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    response_data = response.json()['detail']
    assert response_data == 'You do not have permission to delete this user!'
