
from config.db_config import get_connection


def load_stock_data(ticker, df):
    """
    Saves stock price data into MySQL database.
    
    ticker = stock symbol like "AAPL"
    df = DataFrame from data_fetcher (has Open, High, Low, Close, Volume)
    
    How it works:
    1. First adds the ticker to the 'stocks' table (if not already there)
    2. Then inserts each day's price into 'stock_prices' table
    3. INSERT IGNORE = if that date already exists, skip it (no duplicates)
    4. Returns how many new rows were added
    """
    conn = get_connection()
    if conn is None:
        return 0

    cursor = conn.cursor()
    rows_inserted = 0

    try:
        # Add ticker to stocks table (IGNORE = skip if already exists)
        cursor.execute(
            "INSERT IGNORE INTO stocks (ticker) VALUES (%s)",
            (ticker,)
        )

        # Insert each day's price data
        for date, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT IGNORE INTO stock_prices 
                    (ticker, date, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    ticker,
                    date.strftime('%Y-%m-%d'),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume'])
                ))
                rows_inserted += cursor.rowcount
            except Exception as e:
                print(f"Error inserting row {date}: {e}")

        # Save all changes to database
        conn.commit()
    finally:
        # Always close connection when done
        cursor.close()
        conn.close()

    return rows_inserted


# This runs only when you test this file directly
if __name__ == "__main__":
    from data.data_fetcher import fetch_stock_data

    # Fetch AAPL data from Yahoo Finance
    df = fetch_stock_data("AAPL", "1y")
    
    # Save it to MySQL
    count = load_stock_data("AAPL", df)
    print(f"Loaded {count} rows into MySQL")