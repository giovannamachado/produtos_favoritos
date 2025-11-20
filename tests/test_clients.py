"""Testes para gerenciamento de clientes."""


def test_list_clients_as_admin(client, admin_token, test_user):
    """Admin pode listar todos os clientes."""
    response = client.get(
        "/clients/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # admin + test_user


def test_list_clients_as_user(client, user_token):
    """Usuário comum não pode listar clientes."""
    response = client.get(
        "/clients/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


def test_get_client_by_id_as_admin(client, admin_token, test_user):
    """Admin pode buscar cliente por ID."""
    response = client.get(
        f"/clients/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email


def test_get_client_nonexistent(client, admin_token):
    """Buscar cliente inexistente retorna 404."""
    response = client.get(
        "/clients/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404


def test_create_client_as_admin(client, admin_token):
    """Admin pode criar novos clientes."""
    response = client.post(
        "/clients/",
        params={"role": "user"},
        json={
            "name": "Created User",
            "email": "created@example.com",
            "password": "password123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "created@example.com"
    assert data["role"] == "user"


def test_create_admin_client(client, admin_token):
    """Admin pode criar outro admin."""
    response = client.post(
        "/clients/",
        params={"role": "admin"},
        json={
            "name": "New Admin",
            "email": "newadmin@example.com",
            "password": "adminpass123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "admin"


def test_create_client_duplicate_email(client, admin_token, test_user):
    """Não pode criar cliente com email duplicado."""
    response = client.post(
        "/clients/",
        json={
            "name": "Duplicate",
            "email": test_user.email,
            "password": "password123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 409


def test_update_client_as_admin(client, admin_token, test_user):
    """Admin pode atualizar qualquer cliente."""
    response = client.patch(
        f"/clients/{test_user.id}",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


def test_update_me_as_user(client, user_token):
    """Usuário pode atualizar próprio perfil."""
    response = client.patch(
        "/clients/me",
        json={"name": "My New Name"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My New Name"


def test_delete_client_as_admin(client, admin_token, test_user):
    """Admin pode deletar clientes."""
    response = client.delete(
        f"/clients/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204


def test_delete_client_as_user(client, user_token, test_admin):
    """Usuário comum não pode deletar clientes."""
    response = client.delete(
        f"/clients/{test_admin.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
