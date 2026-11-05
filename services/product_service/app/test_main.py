from fastapi.testclient import TestClient
from main import app
import pytest


client = TestClient(app)
@pytest.fixture(autouse=True) # pytest runs it automatically before every test.
def use_test_database(monkeypatch):
    monkeypatch.setenv( # temporarily changes an environment variable.
        "MYSQL_DATABASE",
        "localmarket_products_test", # tests use localmarket_products_test.
    ) # After each test, pytest restores the original environment variable.

# Add a reusable test-product fixture. This fixture creates a product and gives its data to whichever test requests it.
# Make the tests clean up after themselves
@pytest.fixture
def test_product():
    response = client.post(
        "/products",
        json={
            "name": "Temporary Test Product",
            "description": "Used for automated testing",
            "price": 20.00,
            "shop_name": "Test Shop",
        },
    )

    assert response.status_code == 201

    product = response.json()

    yield product

    client.delete(f"/products/{product['id']}")


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to LocalMarket!"
    }

# test Product listing
def test_get_products():
    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert "products" in data
    assert "total" in data
    assert isinstance(data["products"], list)

# Test a missing product
def test_get_product_not_found():
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }

# Test invalid product creation
def test_create_product_invalid_data():
    response = client.post(
        "/products",
        json={
            "name": "",
            "description": "Invalid product",
            "price": -5.00,
            "shop_name": "Test Shop",
        },
    )

    assert response.status_code == 422 # HTTP 422 Unprocessable Entity means the request reached FastAPI, but the submitted data failed validation.

# TEST SUCCESSFUL EVENTS

# Test successful product creation
def test_create_product():
    response = client.post(
        "/products",
        json={
            "name": "Test Ceramic Vase",
            "description": "A vase created during automated testing",
            "price": 35.50,
            "shop_name": "Test Shop",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Ceramic Vase"
    assert data["price"] == 35.50
    assert data["shop_name"] == "Test Shop"
    assert "id" in data

    client.delete(f"/products/{data['id']}")


# Test product updating
def test_update_product(test_product):
    product_id = test_product["id"]

    response = client.put(
        f"/products/{product_id}",
        json={"price": 45.00},
    )

    assert response.status_code == 200
    assert response.json()["price"] == 45.00
    assert response.json()["name"] == "Temporary Test Product"

# Test product deletion
def test_delete_product(test_product):
    product_id = test_product["id"]

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 404
