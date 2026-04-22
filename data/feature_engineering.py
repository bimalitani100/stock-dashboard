import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features for ML model.
    """
    if df.empty:
        return df

    df = df.copy()

    close_col = "Close" if "Close" in df.columns else "close"
    high_col = "High" if "High" in df.columns else "high"
    low_col = "Low" if "Low" in df.columns else "low"
    volume_col = "Volume" if "Volume" in df.columns else "volume"

    df["ma_20"] = df[close_col].rolling(window=20).mean()
    df["ma_50"] = df[close_col].rolling(window=50).mean()
    df["rsi_14"] = compute_rsi(df[close_col], 14)
    df["volume_ma_20"] = df[volume_col].rolling(window=20).mean()
    df["daily_return"] = df[close_col].pct_change() * 100
    df["price_change"] = df[close_col].diff()
    df["high_low_spread"] = df[high_col] - df[low_col]
    df["close_lag_1"] = df[close_col].shift(1)
    df["close_lag_3"] = df[close_col].shift(3)
    df["close_lag_5"] = df[close_col].shift(5)
    df["target"] = df[close_col].shift(-1)

    df.dropna(inplace=True)
    return df


if __name__ == "__main__":
    from data.data_fetcher import fetch_stock_data

    raw = fetch_stock_data("AAPL", "1y")
    featured = compute_features(raw)
    print(featured.head())
    print(featured.columns.tolist())