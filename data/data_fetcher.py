import pandas as pd
import yfinance as yf


def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance.

    Valid example periods:
    5d, 1mo, 3mo, 6mo, 1y, 2y
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty:
            print(f"No data found for {ticker}")
            return pd.DataFrame()

        df = df.reset_index()
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    sample = fetch_stock_data("AAPL", "1y")
    print(sample.head())
    print(f"Rows fetched: {len(sample)}")