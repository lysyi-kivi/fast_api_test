import pytest

async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

async def test_get_products(client):
    response = await client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_product_not_found(client):
    response = await client.get("/products/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Товар не найден"

async def test_register_user(client):
    response = await client.post("/users/register", json={
        "username": "testuser_pytest",
        "email": "pytest@test.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser_pytest"
    assert "password" not in response.json()