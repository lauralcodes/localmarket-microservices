
from fastapi import FastAPI, HTTPException

from database import get_database_connection


app = FastAPI(title="LocalMarket Product Service")


@app.get("/")
def home():
    return {"message": "Welcome to LocalMarket!"}


@app.get("/products")
def get_products():
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()

        return {"products": products}

    finally:
        connection.close()


@app.get("/products/{product_id}")
def get_product(product_id: int):
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,)
            )
            product = cursor.fetchone()

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        return product

    finally:
        connection.close()
