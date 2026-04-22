from config.db_config import get_connection


def load_stock_data(ticker, df, company_name=None):
    """
    Load fetched stock data into MySQL.
    """
    conn = get_connection()
    if conn is None or df.empty:
        return 0

    cursor = conn.cursor()
    rows_inserted = 0

    try:
        cursor.execute(
            """
            INSERT INTO stocks (ticker, company_name)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE company_name = COALESCE(VALUES(company_name), company_name)
            """,
            (ticker, company_name),
        )

        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT IGNORE INTO stock_prices
                (ticker, date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    ticker,
                    row["Date"].strftime("%Y-%m-%d"),
                    float(row["Open"]),
                    float(row["High"]),
                    float(row["Low"]),
                    float(row["Close"]),
                    int(row["Volume"]),
                ),
            )
            rows_inserted += cursor.rowcount

        conn.commit()
        return rows_inserted
    except Exception as e:
        conn.rollback()
        print(f"Error loading stock data: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    from data.data_fetcher import fetch_stock_data

    ticker = "AAPL"
    df = fetch_stock_data(ticker, "1y")
    count = load_stock_data(ticker, df, "Apple Inc.")
    print(f"Inserted {count} rows.")