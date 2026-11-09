import os

import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_database_connection():
    try:
        connection = pymysql.connect(
            host="127.0.0.1",
            port=3307,
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_SHOPS_DATABASE"),
            cursorclass=pymysql.cursors.DictCursor
        )

        return connection

    except pymysql.MySQLError as error:
        print(f"Shop database connection error: {error}")
        raise