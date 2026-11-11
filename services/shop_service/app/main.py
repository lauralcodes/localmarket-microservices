import pymysql

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from database import get_database_connection
from schemas import ShopCreate, ShopUpdate, ShopResponse, ShopImageCreate, ShopImageResponse


app = FastAPI(title="LocalMarket Shop Service")

# Global database exception handler -It catches MySQL-related errors that are not handled elsewhere in the application
@app.exception_handler(pymysql.MySQLError)
async def database_exception_handler(request: Request, exc: pymysql.MySQLError):
    return JSONResponse(
        status_code=503, # Service Unavailable
        content={"detail": "Database service is temporarily unavailable"},
    )


@app.get("/")
def home():
    return {"message": "Welcome to LocalMarket Shop Service"}


@app.post("/shops", response_model=ShopResponse, status_code=201)
def create_shop(shop: ShopCreate):
    connection = get_database_connection()

    # SQL INSERT query
    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO shops (
                    name, description, email, phone, website,
                    street_address, city, postal_code, country,
                    logo_url, cover_image_url
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
            """

            cursor.execute(
                query,
                (
                    shop.name,
                    shop.description,
                    str(shop.email),
                    shop.phone,
                    str(shop.website) if shop.website else None,
                    shop.street_address,
                    shop.city,
                    shop.postal_code,
                    shop.country,
                    str(shop.logo_url) if shop.logo_url else None,
                    str(shop.cover_image_url) if shop.cover_image_url else None,
                ),
            )

            shop_id = cursor.lastrowid

        connection.commit()

        return get_shop_by_id(shop_id)

    # Handling duplicate emails
    except pymysql.IntegrityError as error: # IntegrityError: Occurs when a database constraint is violated.
        connection.rollback() # Reverses the current transaction.

        if error.args[0] == 1062: # Error code 1062: MySQL duplicate entry error.
            raise HTTPException(
                status_code=409, # HTTP 409: Conflict.
                detail="A shop with this email already exists",
            )

        raise

    finally:
        connection.close()


@app.get("/shops")
def get_shops():
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM shops ORDER BY id DESC")
            shops = cursor.fetchall()

        return shops

    finally:
        connection.close()


@app.get("/shops/{shop_id}", response_model=ShopResponse)
def get_shop_by_id(shop_id: int):
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM shops WHERE id = %s",
                (shop_id,),
            )
            shop = cursor.fetchone()

        if shop is None:
            raise HTTPException(status_code=404, detail="Shop not found")

        return shop

    finally:
        connection.close()


@app.patch("/shops/{shop_id}", response_model=ShopResponse)
def update_shop(shop_id: int, shop: ShopUpdate):
    update_data = shop.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    if "email" in update_data and update_data["email"] is not None:
        update_data["email"] = str(update_data["email"])

    for field in ("website", "logo_url", "cover_image_url"):
        if field in update_data and update_data[field] is not None:
            update_data[field] = str(update_data[field])

    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM shops WHERE id = %s",
                (shop_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Shop not found")

            columns = ", ".join(
                f"{field} = %s" for field in update_data
            )

            values = list(update_data.values())
            values.append(shop_id)

            query = f"UPDATE shops SET {columns} WHERE id = %s"

            cursor.execute(query, values)

        connection.commit()

        return get_shop_by_id(shop_id)

    except pymysql.IntegrityError as error:
        connection.rollback()

        if error.args[0] == 1062:
            raise HTTPException(
                status_code=409,
                detail="A shop with this email already exists",
            )

        raise

    finally:
        connection.close()


@app.delete("/shops/{shop_id}")
def delete_shop(shop_id: int):
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM shops WHERE id = %s",
                (shop_id,),
            )

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Shop not found")

        connection.commit()

        return {"message": "Shop deleted successfully"}

    finally:
        connection.close()



# CRUD operations for shop images

@app.post(
    "/shops/{shop_id}/images",
    response_model=ShopImageResponse,
    status_code=201,
)
def add_shop_image(shop_id: int, image: ShopImageCreate):
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            # First, check that the shop exists.
            cursor.execute(
                "SELECT id FROM shops WHERE id = %s",
                (shop_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Shop not found",
                )

            # Add the image to the shop's gallery.
            cursor.execute(
                """
                INSERT INTO shop_images (
                    shop_id, image_url, alt_text, display_order
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    shop_id,
                    str(image.image_url),
                    image.alt_text,
                    image.display_order,
                ),
            )

            image_id = cursor.lastrowid

            # Retrieve the newly created image.
            cursor.execute(
                "SELECT * FROM shop_images WHERE id = %s",
                (image_id,),
            )
            new_image = cursor.fetchone()

        connection.commit()
        return new_image

    finally:
        connection.close()


@app.get(
    "/shops/{shop_id}/images",
    response_model=list[ShopImageResponse],
)
def get_shop_images(shop_id: int):
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM shops WHERE id = %s",
                (shop_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Shop not found",
                )

            cursor.execute(
                """
                SELECT * FROM shop_images
                WHERE shop_id = %s
                ORDER BY display_order ASC, id ASC
                """,
                (shop_id,),
            )

            images = cursor.fetchall()

        return images

    finally:
        connection.close()


@app.delete("/shops/{shop_id}/images/{image_id}")
def delete_shop_image(shop_id: int, image_id: int):
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM shops WHERE id = %s",
                (shop_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Shop not found",
                )

            cursor.execute(
                """
                DELETE FROM shop_images
                WHERE id = %s AND shop_id = %s
                """,
                (image_id, shop_id),
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Shop image not found",
                )

        connection.commit()

        return {"message": "Shop image deleted successfully"}

    finally:
        connection.close()