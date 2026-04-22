from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow,
    QLabel,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QMessageBox,
)

from alerts.alert_service import AlertService
from config.db_config import get_connection
from dashboard.chart_widget import PriceChartWidget
from data.data_fetcher import fetch_stock_data
from data.data_loader import load_stock_data
from data.feature_engineering import compute_features
from ml.model_trainer import ModelTrainer
from ml.predictor import predict_future
from utils.recommendation_service import RecommendationService


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current_period = "1y"
        self.raw_df = None
        self.featured_df = None
        self.alert_service = AlertService()
        self.model_trainer = ModelTrainer()

        self.setWindowTitle("Stock Price Prediction Dashboard")
        self.setGeometry(100, 100, 1280, 820)

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7fb; }
            QLabel { color: #1f2937; }
            QFrame#sidebar {
                background-color: #ffffff;
                border: 1px solid #dbe2ea;
                border-radius: 12px;
            }
            QComboBox, QPushButton {
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #cbd5e1;
            }
            QPushButton {
                background-color: #e5e7eb;
                border: none;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #d1d5db;
            }
        """)

        self._build_ui()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        sidebar = self._create_sidebar()
        content = self._create_content_area()

        main_layout.addWidget(sidebar, 1)
        main_layout.addWidget(content, 3)

    def _create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(280)
        sidebar.setMaximumWidth(340)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        sidebar.setLayout(layout)

        title = QLabel("Dashboard Controls")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        user_label = QLabel(f"Welcome: {self.user['username']} ({self.user['role']})")
        user_label.setFont(QFont("Arial", 10))

        ticker_label = QLabel("Select Ticker")
        ticker_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        self.ticker_dropdown = QComboBox()
        self.ticker_dropdown.addItems([
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "META", "NVDA", "JPM", "V", "DIS"
        ])

        range_label = QLabel("Select Date Range")
        range_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        self.btn_1w = QPushButton("1W")
        self.btn_1m = QPushButton("1M")
        self.btn_3m = QPushButton("3M")
        self.btn_1y = QPushButton("1Y")

        self.btn_1w.clicked.connect(lambda: self.update_range("1 Week", "5d"))
        self.btn_1m.clicked.connect(lambda: self.update_range("1 Month", "1mo"))
        self.btn_3m.clicked.connect(lambda: self.update_range("3 Months", "3mo"))
        self.btn_1y.clicked.connect(lambda: self.update_range("1 Year", "1y"))

        self.selected_range_label = QLabel("Current Range: 1 Year")

        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.clicked.connect(self.handle_fetch_data)

        self.predict_button = QPushButton("Run Prediction")
        self.predict_button.clicked.connect(self.handle_prediction)

        layout.addWidget(title)
        layout.addWidget(user_label)
        layout.addSpacing(8)
        layout.addWidget(ticker_label)
        layout.addWidget(self.ticker_dropdown)
        layout.addSpacing(8)
        layout.addWidget(range_label)
        layout.addWidget(self.btn_1w)
        layout.addWidget(self.btn_1m)
        layout.addWidget(self.btn_3m)
        layout.addWidget(self.btn_1y)
        layout.addWidget(self.selected_range_label)
        layout.addSpacing(8)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.predict_button)
        layout.addStretch()

        return sidebar

    def _create_content_area(self):
        wrapper = QWidget()
        layout = QVBoxLayout()
        wrapper.setLayout(layout)

        self.chart_widget = PriceChartWidget()
        self.chart_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Arial", 11))

        self.metrics_label = QLabel("Metrics: Not computed yet")
        self.metrics_label.setWordWrap(True)

        self.alerts_label = QLabel("Alerts: None")
        self.alerts_label.setWordWrap(True)

        self.recommendation_label = QLabel("Recommendation: Not available yet")
        self.recommendation_label.setWordWrap(True)

        layout.addWidget(self.chart_widget)
        layout.addWidget(self.status_label)
        layout.addWidget(self.metrics_label)
        layout.addWidget(self.alerts_label)
        layout.addWidget(self.recommendation_label)

        return wrapper

    def update_range(self, label, period_code):
        self.current_period = period_code
        ticker = self.ticker_dropdown.currentText()
        self.selected_range_label.setText(f"Current Range: {label} | Ticker: {ticker}")

    def handle_fetch_data(self):
        ticker = self.ticker_dropdown.currentText()
        self.status_label.setText(f"Status: Fetching data for {ticker}...")

        self.raw_df = fetch_stock_data(ticker, self.current_period)

        if self.raw_df.empty:
            QMessageBox.warning(self, "No Data", "No stock data was fetched.")
            self.status_label.setText("Status: Failed to fetch data.")
            return

        load_stock_data(ticker, self.raw_df)
        self.featured_df = compute_features(self.raw_df)
        if self.featured_df is not None and not self.featured_df.empty:
            self.chart_widget.update_chart(self.featured_df)
        else:
            self.chart_widget.update_chart(self.raw_df)

        self.status_label.setText(f"Status: Data fetched and loaded for {ticker}.")

    def handle_prediction(self):
        if self.featured_df is None or self.featured_df.empty:
            QMessageBox.warning(self, "Missing Data", "Please fetch data first.")
            return

        X_train, X_test, y_train, y_test = self.model_trainer.prepare_data(self.featured_df)
        model = self.model_trainer.train_linear_regression(X_train, y_train)
        metrics = self.model_trainer.evaluate_model(model, X_test, y_test)

        prediction_df = predict_future(
            self.featured_df,
            model,
            self.model_trainer.FEATURE_COLUMNS,
            days=7,
        )

        self.chart_widget.show_predictions(self.featured_df, prediction_df)
        self.metrics_label.setText(
            f"Metrics: MAE={metrics['MAE']} | RMSE={metrics['RMSE']} | R²={metrics['R2']}"
        )

        current_price = float(self.featured_df.iloc[-1]["Close"])
        previous_price = float(self.featured_df.iloc[-2]["Close"])
        alerts = self.alert_service.check_price_change(
            self.ticker_dropdown.currentText(),
            current_price,
            previous_price,
        )

        if alerts:
            msg = alerts[0]["message"]
            self.alerts_label.setText(f"Alerts: {msg}")
            self.alert_service.notify_users_for_stock(
                self.ticker_dropdown.currentText(),
                msg,
                alerts[0]["percent_change"],
            )
        else:
            self.alerts_label.setText("Alerts: No alert triggered")

        profile = self._get_user_profile(self.user["id"])
        trend = "bullish" if prediction_df["predicted_close"].iloc[-1] > current_price else "bearish"
        recommendation = RecommendationService.generate_recommendation(profile, prediction_df, trend)
        self.recommendation_label.setText(f"Recommendation: {recommendation}")

        self.status_label.setText("Status: Prediction completed.")

    def _get_user_profile(self, user_id):
        conn = get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM customer_profiles WHERE user_id = %s",
                (user_id,),
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None
        finally:
            cursor.close()
            conn.close()