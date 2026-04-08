
import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker, period="1y"):
    """
    Downloads stock price data from Yahoo Finance.
    
    ticker = stock symbol like "AAPL" for Apple, "GOOGL" for Google
    period = how far back to get data: "1wk", "1mo", "3mo", "1y"
    
    Returns a DataFrame with columns: Open, High, Low, Close, Volume
    - Open: price when market opened that day
    - High: highest price that day
    - Low: lowest price that day
    - Close: price when market closed that day
    - Volume: how many shares were traded that day
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            print(f"Warning: No data found for {ticker}")
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()


# This runs only when you test this file directly
if __name__ == "__main__":
    df = fetch_stock_data("AAPL", "1y")
    print(f"Fetched {len(df)} rows for AAPL")
    print(df.head())