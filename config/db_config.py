import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


def get_connection(database: str | None = None):
    """
    Returns a MySQL connection using values from .env
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=database or os.getenv("DB_NAME", "stock_dashboard"),
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None


def initialize_database():
    """
    Creates the database if it does not already exist.
    """
    db_name = os.getenv("DB_NAME", "stock_dashboard")
    conn = get_connection(database=None)
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Failed to initialize database: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    if initialize_database():
        print("Database checked/created successfully.")

    conn = get_connection()
    if conn:
        print("Connected to MySQL successfully!")
        conn.close()
    else:
        print("Connection failed. Check your .env file.")