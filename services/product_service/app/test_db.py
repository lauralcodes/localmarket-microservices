from database import get_database_connection

connection = get_database_connection()

print("Successfully connected to LocalMarket MySQL!")

connection.close()
