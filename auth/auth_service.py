import hashlib
from config.db_config import get_connection


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self, username: str, password: str):
        conn = get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
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

    def create_default_users(self):
        conn = get_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()

            stocks = [
                ("AAPL", "Apple Inc."),
                ("GOOGL", "Alphabet Inc."),
                ("MSFT", "Microsoft Corp."),
                ("AMZN", "Amazon.com Inc."),
                ("TSLA", "Tesla Inc."),
                ("META", "Meta Platforms Inc."),
                ("NVDA", "NVIDIA Corp."),
                ("JPM", "JPMorgan Chase & Co."),
                ("V", "Visa Inc."),
                ("DIS", "Walt Disney Co."),
            ]

            for ticker, company in stocks:
                cursor.execute(
                    """
                    INSERT IGNORE INTO stocks (ticker, company_name)
                    VALUES (%s, %s)
                    """,
                    (ticker, company),
                )

            users = [("agent", self.hash_password("agent123"), "agent")]

            for i in range(1, 11):
                users.append((f"customer{i}", self.hash_password(f"cust{i}123"), "customer"))

            for username, password_hash, role in users:
                cursor.execute(
                    """
                    INSERT IGNORE INTO users (username, password_hash, role)
                    VALUES (%s, %s, %s)
                    """,
                    (username, password_hash, role),
                )

            conn.commit()
            self.create_customer_profiles_and_holdings()

        except Exception as e:
            conn.rollback()
            print(f"Error creating default users: {e}")
        finally:
            cursor.close()
            conn.close()

    def create_customer_profiles_and_holdings(self):
        conn = get_connection()
        if conn is None:
            return

        customer_holdings = {
            "customer1": [("AAPL", 5, 180.00), ("MSFT", 3, 310.00)],
            "customer2": [("TSLA", 2, 220.00), ("NVDA", 1, 700.00)],
            "customer3": [("GOOGL", 4, 135.00), ("AMZN", 2, 145.00)],
            "customer4": [("META", 3, 320.00), ("AAPL", 2, 175.00)],
            "customer5": [("JPM", 6, 150.00), ("V", 4, 240.00)],
            "customer6": [("DIS", 5, 95.00), ("MSFT", 2, 305.00)],
            "customer7": [("NVDA", 2, 650.00), ("TSLA", 1, 210.00)],
            "customer8": [("AMZN", 3, 140.00), ("GOOGL", 2, 130.00)],
            "customer9": [("V", 5, 235.00), ("JPM", 3, 145.00)],
            "customer10": [("META", 2, 310.00), ("DIS", 4, 90.00)],
        }

        risk_profiles = [
            "low", "medium", "high", "medium", "low",
            "medium", "high", "medium", "low", "high"
        ]

        try:
            cursor = conn.cursor(dictionary=True)

            for index, username in enumerate(customer_holdings.keys()):
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if not user:
                    continue

                user_id = user["id"]
                risk = risk_profiles[index]

                cursor.execute(
                    """
                    INSERT IGNORE INTO customer_profiles
                    (user_id, monthly_income, monthly_expenses, savings, debt,
                     investment_budget, risk_tolerance, time_horizon)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        3000 + (index * 250),
                        1800 + (index * 100),
                        4000 + (index * 500),
                        1000,
                        400 + (index * 50),
                        risk,
                        "medium-term",
                    ),
                )

                for ticker, qty, avg_price in customer_holdings[username]:
                    cursor.execute(
                        """
                        INSERT INTO holdings (user_id, ticker, quantity, average_buy_price)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            quantity = VALUES(quantity),
                            average_buy_price = VALUES(average_buy_price)
                        """,
                        (user_id, ticker, qty, avg_price),
                    )

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Error creating profiles and holdings: {e}")
        finally:
            cursor.close()
            conn.close()