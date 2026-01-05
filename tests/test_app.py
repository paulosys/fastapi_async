from http import HTTPStatus

from schemas import UserOutSchema


def test_read_root_should_return_hello_world(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}


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


def test_list_users_should_return_all_users(client, user):

    user_schema = UserOutSchema.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['users'] == [user_schema]


def test_update_user_should_return_updated_user(client, user):
    payload = {
        'username': 'updatableuser',
        'email': 'updatableuser@example.com',
        'password': 'securepassword123',
    }

    response = client.put(f'/users/{user.id}', json=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['username'] == payload['username']
    assert response_data['email'] == payload['email']
    assert response_data['id'] == user.id


def test_update_user_with_existing_email_should_return_409(client, user):
    client.post(
        '/users/',
        json={
            'username': 'anotheruser',
            'email': 'anotheruser@example.com',
            'password': 'securepassword123',
        },
    )

    payload = {
        'username': user.username,
        'email': 'anotheruser@example.com',
        'password': 'securepassword123',
    }

    response = client.put(f'/users/{user.id}', json=payload)

    assert response.status_code == HTTPStatus.CONFLICT
    response_data = response.json()['detail']
    assert response_data == 'User with this email or username already exists!'


def test_update_nonexistent_user_should_return_404(client):
    payload = {
        'username': 'nonexistentuser',
        'email': 'nonexistentuser@example.com',
        'password': 'securepassword123',
    }

    response = client.put('/users/999', json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND
    response_data = response.json()
    assert response_data['detail'] == 'User not found!'


def test_delete_user_should_return_no_content(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['message'] == 'User deleted successfully!'


def test_delete_nonexistent_user_should_return_404(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    response_data = response.json()
    assert response_data['detail'] == 'User not found!'
