from config.db_config import get_connection


class AlertService:
    def create_alert(self, ticker, alert_type, threshold):
        conn = get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO alerts (ticker, alert_type, threshold, is_active)
                VALUES (%s, %s, %s, TRUE)
                """,
                (ticker, alert_type, threshold),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            print(f"Error creating alert: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def check_price_change(self, ticker, current_price, previous_price):
        if previous_price == 0:
            return []

        percent_change = ((current_price - previous_price) / previous_price) * 100
        triggered = []

        if abs(percent_change) >= 2:
            message = f"{ticker} moved {percent_change:.2f}%"
            triggered.append({
                "ticker": ticker,
                "percent_change": round(percent_change, 2),
                "message": message,
            })

        return triggered

    def notify_users_for_stock(self, ticker, message, triggered_value, alert_id=None):
        conn = get_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT DISTINCT u.id
                FROM users u
                LEFT JOIN holdings h ON u.id = h.user_id
                WHERE u.role = 'agent' OR h.ticker = %s
                """,
                (ticker,),
            )
            users = cursor.fetchall()

            insert_cursor = conn.cursor()
            for user in users:
                insert_cursor.execute(
                    """
                    INSERT INTO alert_history (alert_id, user_id, ticker, triggered_value, message, is_read)
                    VALUES (%s, %s, %s, %s, %s, FALSE)
                    """,
                    (alert_id, user["id"], ticker, triggered_value, message),
                )

            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error notifying users: {e}")
        finally:
            cursor.close()
            insert_cursor.close()
            conn.close()

    def get_alert_history(self, user_id=None, limit=20):
        conn = get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor(dictionary=True)

            if user_id:
                cursor.execute(
                    """
                    SELECT * FROM alert_history
                    WHERE user_id = %s
                    ORDER BY triggered_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM alert_history
                    ORDER BY triggered_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )

            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching alert history: {e}")
            return []
        finally:
            cursor.close()
            conn.close()