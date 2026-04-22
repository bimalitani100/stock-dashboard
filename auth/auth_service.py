import hashlib
from config.db_config import get_connection


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_default_users(self):
        conn = get_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()

            users = [
                ("agent", self.hash_password("agent123"), "agent"),
                ("customer1", self.hash_password("cust123"), "customer"),
            ]

            for username, password_hash, role in users:
                cursor.execute(
                    """
                    INSERT IGNORE INTO users (username, password_hash, role)
                    VALUES (%s, %s, %s)
                    """,
                    (username, password_hash, role),
                )

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Error creating default users: {e}")

        finally:
            cursor.close()
            conn.close()

    def authenticate_user(self, username: str, password: str):
        conn = get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,),
            )

            user = cursor.fetchone()

            if not user:
                return None

            if user["password_hash"] != self.hash_password(password):
                return None

            return user

        except Exception as e:
            print(f"Authentication error: {e}")
            return None

        finally:
            cursor.close()
            conn.close()