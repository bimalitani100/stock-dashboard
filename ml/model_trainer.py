from pathlib import Path
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class ModelTrainer:
    FEATURE_COLUMNS = [
        "ma_20",
        "ma_50",
        "rsi_14",
        "volume_ma_20",
        "daily_return",
        "price_change",
        "high_low_spread",
        "close_lag_1",
        "close_lag_3",
        "close_lag_5",
    ]

    def prepare_data(self, df, train_ratio=0.8):
        X = df[self.FEATURE_COLUMNS]
        y = df["target"]

        split_index = int(len(df) * train_ratio)

        X_train = X.iloc[:split_index]
        X_test = X.iloc[split_index:]
        y_train = y.iloc[:split_index]
        y_test = y.iloc[split_index:]

        return X_train, X_test, y_train, y_test

    def train_linear_regression(self, X, y):
        model = LinearRegression()
        model.fit(X, y)
        return model

    def train_random_forest(self, X, y):
        model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=8,
        )
        model.fit(X, y)
        return model

    def evaluate_model(self, model, X, y):
        predictions = model.predict(X)

        mae = mean_absolute_error(y, predictions)
        rmse = mean_squared_error(y, predictions) ** 0.5
        r2 = r2_score(y, predictions)

        return {
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "R2": round(r2, 4),
        }

    def save_model(self, model, filename):
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump(model, f)

    def load_model(self, filename):
        with open(filename, "rb") as f:
            return pickle.load(f)