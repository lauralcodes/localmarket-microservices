from database import get_database_connection


def test_shop_database_connection():
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE() AS database_name")
            result = cursor.fetchone()

        assert result["database_name"] == "localmarket_shops"

    finally:
        connection.close()