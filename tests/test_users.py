from http import HTTPStatus

from schemas import UserOutSchema


def test_create_user_should_return_created_user(client):
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


def test_create_user_with_existing_email_should_return_409(client, user):
    payload = {
        'username': 'newuser',
        'email': user.email,
        'password': 'anotherpassword123',
    }

    response = client.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CONFLICT
    response_data = response.json()['detail']
    assert response_data == 'User with this email or username already exists!'


def test_list_users_should_return_all_users(client, user, token):
    user_schema = UserOutSchema.model_validate(user).model_dump()

    response = client.get(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['users'] == [user_schema]


def test_update_user_should_return_updated_user(client, user, token):
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


def test_update_user_with_existing_email_should_return_409(
    client,
    user,
    token,
):
    client.post(
        '/users/',
        json={
            'username': 'anotheruser',
            'email': 'anotheruser@example.com',
            'password': 'securepassword123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    payload = {
        'username': user.username,
        'email': 'anotheruser@example.com',
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


def test_update_other_user_should_return_403(
    client,
    user,
    token,
):
    # Create another user
    response = client.post(
        '/users/',
        json={
            'username': 'otheruser',
            'email': 'otheruser@example.com',
            'password': 'securepassword123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    other_user_id = response.json()['id']

    payload = {
        'username': 'hackeruser',
        'email': 'hackeruser@example.com',
        'password': 'securepassword123',
    }

    response = client.put(
        f'/users/{other_user_id}',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    response_data = response.json()['detail']
    assert response_data == 'You do not have permission to update this user!'


def test_delete_user_should_return_no_content(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['message'] == 'User deleted successfully!'


def test_delete_other_user_should_return_403(
    client,
    user,
    token,
):
    # Create another user
    response = client.post(
        '/users/',
        json={
            'username': 'otheruser',
            'email': 'otheruser@example.com',
            'password': 'securepassword123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    other_user_id = response.json()['id']

    response = client.delete(
        f'/users/{other_user_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    response_data = response.json()['detail']
    assert response_data == 'You do not have permission to delete this user!'
