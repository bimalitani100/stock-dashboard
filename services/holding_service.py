from config.db_config import get_connection


class HoldingService:
    def get_customers(self):
        conn = get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, username, role
                FROM users
                WHERE role = 'customer'
                ORDER BY username
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching customers: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_customer_holdings(self, user_id):
        conn = get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT ticker, quantity, average_buy_price
                FROM holdings
                WHERE user_id = %s
                ORDER BY ticker
                """,
                (user_id,),
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching holdings: {e}")
            return []
        finally:
            cursor.close()
            conn.close()