
from fastapi import FastAPI, HTTPException
from database import get_database_connection
from schemas import ProductCreate
from schemas import ProductUpdate


app = FastAPI(title="LocalMarket Product Service")



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

@app.post("/products", status_code=201)
def create_product(product: ProductCreate):
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO products (name, description, price, shop_name)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    product.name,
                    product.description,
                    product.price,
                    product.shop_name,
                ),
            )

            connection.commit()

            new_product_id = cursor.lastrowid

            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (new_product_id,),
            )

            new_product = cursor.fetchone()

        return new_product

    finally:
        connection.close()


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    updates = product.model_dump(exclude_unset=True) # get only the fields that were provided in the request. if someone updates only the price, we must preserve the existing name, description and shop.

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM products WHERE id = %s",
                (product_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found",
                )

            fields = ", ".join(f"{field} = %s" for field in updates)
            values = list(updates.values())
            values.append(product_id)

            cursor.execute(
                f"UPDATE products SET {fields} WHERE id = %s",
                values,
            )

            connection.commit()

            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,),
            )

            updated_product = cursor.fetchone()

        return updated_product

    finally:
        connection.close()        


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM products WHERE id = %s",
                (product_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Product is not found",
                )

            cursor.execute(
                "DELETE FROM products WHERE id = %s",
                (product_id,),
            )

            connection.commit()

        return {"message": "Product deleted successfully"}

    finally:
        connection.close()    