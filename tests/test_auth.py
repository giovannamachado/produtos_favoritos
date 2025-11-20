"""Testes para autenticação."""


def test_register_success(client):
    """Testa registro de novo cliente."""
    response = client.post(
        "/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New User"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "user"
    assert "password" not in data


def test_register_duplicate_email(client, test_user):
    """Testa registro com email duplicado."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Another User",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 409
    assert "já cadastrado" in response.json()["detail"]


def test_login_success(client, test_user):
    """Testa login com credenciais válidas."""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Testa login com credenciais inválidas."""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Testa login com usuário inexistente."""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "password123"}
    )
    assert response.status_code == 401


def test_get_me_authenticated(client, user_token):
    """Testa endpoint /me com autenticação."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


def test_get_me_unauthenticated(client):
    """Testa endpoint /me sem autenticação."""
    response = client.get("/auth/me")
    assert response.status_code == 401
