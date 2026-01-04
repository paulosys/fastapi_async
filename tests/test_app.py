from http import HTTPStatus


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


def test_list_users_should_return_all_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert 'users' in response_data
    assert isinstance(response_data['users'], list)


def test_update_user_should_return_updated_user(client):
    payload = {
        'username': 'updatableuser',
        'email': 'updatableuser@example.com',
        'password': 'securepassword123',
    }

    response = client.put('/users/1', json=payload)

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['username'] == payload['username']
    assert response_data['email'] == payload['email']
    assert response_data['id'] == 1


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


def test_delete_user_should_return_no_content(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_nonexistent_user_should_return_404(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    response_data = response.json()
    assert response_data['detail'] == 'User not found!'
