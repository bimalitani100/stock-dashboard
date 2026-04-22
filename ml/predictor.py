import pandas as pd


def predict_future(df, model, feature_columns, days=7):
    """
    Predict future closing prices using latest available features.
    This is a simplified class-project version.
    """
    if df.empty:
        return pd.DataFrame()

    latest_row = df.iloc[-1:].copy()
    results = []

    current_features = latest_row[feature_columns].copy()

    for day in range(1, days + 1):
        predicted_price = float(model.predict(current_features)[0])

        results.append({
            "day": day,
            "predicted_close": round(predicted_price, 2),
        })

        current_features["close_lag_1"] = predicted_price
        current_features["close_lag_3"] = predicted_price
        current_features["close_lag_5"] = predicted_price

    return pd.DataFrame(results)