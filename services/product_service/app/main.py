
from fastapi import FastAPI
from fastapi import HTTPException


app = FastAPI(title="LocalMarket Product Service")


@app.get("/")
def home():
    return {"message": "Welcome to LocalMarket!"}


from fastapi import FastAPI

app = FastAPI(title="LocalMarket Product Service")


@app.get("/")
def home():
    return {"message": "Welcome to LocalMarket!"}


@app.get("/products")
def get_products():
    products = [
        {
            "id": 1,
            "name": "Handmade Ceramic Mug",
            "price": 15.00,
            "shop": "Anna's Crafts",
        },
        {
            "id": 2,
            "name": "Organic Apple Jam",
            "price": 8.50,
            "shop": "Local Farm Foods",
        },
    ]

    return {"products": products}


from fastapi import HTTPException


@app.get("/products/{product_id}")
def get_product(product_id: int):
    products = [
        {
            "id": 1,
            "name": "Handmade Ceramic Mug",
            "price": 15.00,
            "shop": "Anna's Crafts",
        },
        {
            "id": 2,
            "name": "Organic Apple Jam",
            "price": 8.50,
            "shop": "Local Farm Foods",
        },
    ]

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found",
    )
