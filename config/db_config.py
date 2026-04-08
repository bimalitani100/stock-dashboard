import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "stock_dashboard")
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None


if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("Connected to MySQL successfully!")
        conn.close()
    else:
        print("Connection failed. Check your .env file.")