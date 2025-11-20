"""Testes para favoritos."""
from unittest.mock import AsyncMock, patch


@patch("produtos_favoritos.products_service.fetch_external_product")
def test_add_favorite_success(mock_fetch, client, user_token):
    """Testa adicionar produto aos favoritos."""
    mock_fetch.return_value = {
        "id": 1,
        "title": "Test Product",
        "image": "http://example.com/image.jpg",
        "price": 29.99,
        "rating": {"rate": 4.5, "count": 100}
    }

    response = client.post(
        "/favorites/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["product"]["id"] == 1
    assert data["product"]["title"] == "Test Product"
    assert "rating" in data["product"]["review"].lower()


@patch("produtos_favoritos.products_service.fetch_external_product")
def test_add_favorite_duplicate(mock_fetch, client, user_token):
    """Testa adicionar produto duplicado aos favoritos."""
    mock_fetch.return_value = {
        "id": 1,
        "title": "Test Product",
        "image": "http://example.com/image.jpg",
        "price": 29.99,
        "rating": {"rate": 4.5, "count": 100}
    }

    # Adiciona primeira vez
    client.post(
        "/favorites/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Tenta adicionar novamente
    response = client.post(
        "/favorites/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 409
    assert "já favoritado" in response.json()["detail"]


@patch("produtos_favoritos.products_service.fetch_external_product")
def test_add_favorite_invalid_product(mock_fetch, client, user_token):
    """Testa adicionar produto inexistente."""
    from fastapi import HTTPException

    async def mock_error(*args, **kwargs):
        raise HTTPException(
            status_code=404, detail="Produto não encontrado na API externa")

    mock_fetch.side_effect = mock_error

    response = client.post(
        "/favorites/99999",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404


@patch("produtos_favoritos.products_service.fetch_external_product")
def test_list_favorites(mock_fetch, client, user_token):
    """Testa listagem de favoritos."""
    mock_fetch.return_value = {
        "id": 1,
        "title": "Test Product",
        "image": "http://example.com/image.jpg",
        "price": 29.99,
        "rating": {"rate": 4.5, "count": 100}
    }

    # Adiciona favorito
    client.post(
        "/favorites/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Lista favoritos
    response = client.get(
        "/favorites/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["product"]["id"] == 1


@patch("produtos_favoritos.products_service.fetch_external_product")
def test_remove_favorite_success(mock_fetch, client, user_token):
    """Testa remover favorito."""
    mock_fetch.return_value = {
        "id": 1,
        "title": "Test Product",
        "image": "http://example.com/image.jpg",
        "price": 29.99,
        "rating": {"rate": 4.5, "count": 100}
    }

    # Adiciona favorito
    client.post(
        "/favorites/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Remove favorito
    response = client.delete(
        "/favorites/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 204


def test_remove_favorite_nonexistent(client, user_token):
    """Testa remover favorito inexistente."""
    response = client.delete(
        "/favorites/99999",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404


def test_favorites_require_auth(client):
    """Testa que favoritos exigem autenticação."""
    response = client.get("/favorites/")
    assert response.status_code == 401

    response = client.post("/favorites/1")
    assert response.status_code == 401

    response = client.delete("/favorites/1")
    assert response.status_code == 401
