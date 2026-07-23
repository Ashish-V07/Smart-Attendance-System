import mysql.connector
from mysql.connector import Error
from passwords_db import values

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=values.host,
            user=values.user,
            password=values.password,
            database=values.database
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print("Database Connection Error:", e)
        return None