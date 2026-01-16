from http import HTTPStatus

import pytest

from tests.conftest import TodoFactory


def test_create_todo(client, token):
    payload = {
        'title': 'Test Todo',
        'description': 'This is a test todo item.',
        'state': 'todo',
    }

    response = client.post(
        '/todos/',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['title'] == payload['title']
    assert data['description'] == payload['description']
    assert data['state'] == payload['state']
    assert 'id' in data


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(client, token, session, user):
    expected_todos = 5

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_with_title_filter(client, token, session, user):
    todo_with_special_title = TodoFactory(
        title='SpecialTitle123', user_id=user.id
    )
    session.add_all([
        todo_with_special_title,
        *TodoFactory.create_batch(3, user_id=user.id),
    ])
    await session.commit()

    response = client.get(
        '/todos/?title=SpecialTitle',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == 1
    assert data['todos'][0]['title'] == todo_with_special_title.title


@pytest.mark.asyncio
async def test_list_todos_with_state_filter(client, token, session, user):
    todo_in_doing_state = TodoFactory(state='doing', user_id=user.id)
    session.add_all([
        todo_in_doing_state,
        *TodoFactory.create_batch(4, user_id=user.id, state='todo'),
    ])
    await session.commit()

    response = client.get(
        '/todos/?state=doing',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == 1
    assert data['todos'][0]['state'] == todo_in_doing_state.state


@pytest.mark.asyncio
async def test_list_todos_with_description_filter(
    client, token, session, user
):
    todo_with_special_description = TodoFactory(
        description='UniqueDescription456', user_id=user.id
    )
    session.add_all([
        todo_with_special_description,
        *TodoFactory.create_batch(3, user_id=user.id),
    ])
    await session.commit()

    response = client.get(
        '/todos/?description=UniqueDescription',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == 1
    assert (
        data['todos'][0]['description']
        == todo_with_special_description.description
    )


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    client, token, session, user
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?limit=2&offset=1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'todos' in data
    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_delete_todo(client, token, session, user):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['message'] == 'Task deleted successfully!'


def test_delete_nonexistent_todo(client, token):
    nonexistent_todo_id = 9999

    response = client.delete(
        f'/todos/{nonexistent_todo_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert data['detail'] == 'Task not found'


@pytest.mark.asyncio
async def test_delete_todo_of_another_user(
    client, token, session, another_user
):
    todo = TodoFactory(user_id=another_user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert data['detail'] == 'Task not found'


@pytest.mark.asyncio
async def test_update_todo(client, token, session, user):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    update_payload = {
        'title': 'Updated Title',
        'description': 'Updated Description',
        'state': 'doing',
    }

    response = client.patch(
        f'/todos/{todo.id}',
        json=update_payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['title'] == update_payload['title']
    assert data['description'] == update_payload['description']
    assert data['state'] == update_payload['state']
    assert data['id'] == todo.id


def test_update_nonexistent_todo(client, token):
    nonexistent_todo_id = 8888

    update_payload = {
        'title': 'Should Not Work',
        'description': 'This todo does not exist.',
        'state': 'done',
    }

    response = client.patch(
        f'/todos/{nonexistent_todo_id}',
        json=update_payload,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert data['detail'] == 'Task not found'
