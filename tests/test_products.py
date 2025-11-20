"""Testes para produtos."""
from unittest.mock import AsyncMock, patch


@patch("produtos_favoritos.products_service.fetch_external_product")
def test_get_product_success(mock_fetch, client):
    """Testa buscar produto."""
    mock_fetch.return_value = {
        "id": 1,
        "title": "Test Product",
        "image": "http://example.com/image.jpg",
        "price": 29.99,
        "rating": {"rate": 4.5, "count": 100}
    }

    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Product"
    assert data["price"] == 29.99
    assert data["review"] is not None
    assert "4.5" in data["review"]


@patch("produtos_favoritos.products_service.fetch_external_product")
def test_get_product_not_found(mock_fetch, client):
    """Testa buscar produto inexistente."""
    from fastapi import HTTPException

    async def mock_error(*args, **kwargs):
        raise HTTPException(
            status_code=404, detail="Produto não encontrado na API externa")

    mock_fetch.side_effect = mock_error

    response = client.get("/products/99999")
    assert response.status_code == 404
