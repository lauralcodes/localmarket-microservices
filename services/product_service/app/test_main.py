from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to LocalMarket!"
    }


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