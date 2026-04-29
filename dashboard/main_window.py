from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
)

from alerts.alert_service import AlertService
from config.db_config import get_connection
from dashboard.chart_widget import PriceChartWidget, PredictionMiniChart
from data.data_fetcher import fetch_stock_data
from data.data_loader import load_stock_data
from data.feature_engineering import compute_features
from ml.model_trainer import ModelTrainer
from ml.predictor import predict_future
from services.holding_service import HoldingService
from utils.recommendation_service import RecommendationService


class MainWindow(QMainWindow):
    def __init__(self, user, controller):
        super().__init__()

        self.user = user
        self.controller = controller
        self.role = user["role"]

        self.current_period = "1y"
        self.selected_customer_id = None
        self.selected_ticker = "AAPL"

        self.raw_df = None
        self.featured_df = None

        self.alert_service = AlertService()
        self.model_trainer = ModelTrainer()
        self.holding_service = HoldingService()

        self.supported_tickers = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "META", "NVDA", "JPM", "V", "DIS"
        ]

        self.setWindowTitle(f"Stock Dashboard - {self.role.capitalize()} View")
        self.setGeometry(60, 40, 1550, 920)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #eef2f7;
            }

            QLabel {
                color: #111827;
            }

            QFrame#topBar {
                background-color: #111827;
                border-radius: 14px;
            }

            QFrame#card {
                background-color: white;
                border-radius: 14px;
                border: 1px solid #dbe2ea;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QComboBox {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 7px;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #e5e7eb;
            }

            QHeaderView::section {
                background-color: #f3f4f6;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)

        self._build_ui()

        self.market_timer = QTimer()
        self.market_timer.timeout.connect(self.refresh_market_watch)
        self.market_timer.start(60000)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        central.setLayout(layout)

        layout.addWidget(self._create_top_bar())
        layout.addWidget(self._create_market_watch())

        body = QHBoxLayout()
        body.setSpacing(14)

        body.addWidget(self._create_customer_panel(), 1)
        body.addWidget(self._create_main_panel(), 3)

        layout.addLayout(body)

    def _create_top_bar(self):
        bar = QFrame()
        bar.setObjectName("topBar")

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        bar.setLayout(layout)

        title = QLabel("Stock Monitoring & Prediction Dashboard")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")

        role_text = "Agent Dashboard" if self.role == "agent" else "Customer Dashboard"

        user_info = QLabel(f"{role_text} | Logged in as {self.user['username']}")
        user_info.setStyleSheet("color: #cbd5e1; font-size: 13px;")

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 14px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(user_info)
        layout.addWidget(logout_btn)

        return bar

    def _create_market_watch(self):
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        card.setLayout(layout)

        top = QHBoxLayout()

        title = QLabel("Live Market Watch - 10 Supported Companies")
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))

        refresh_btn = QPushButton("Refresh Market")
        refresh_btn.clicked.connect(self.refresh_market_watch)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(refresh_btn)

        self.market_table = QTableWidget()
        self.market_table.setColumnCount(5)
        self.market_table.setHorizontalHeaderLabels(
            ["Ticker", "Latest Price", "Change %", "Signal", "Alert Status"]
        )
        self.market_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.market_table.setMaximumHeight(190)

        self.market_table.setRowCount(len(self.supported_tickers))

        for row, ticker in enumerate(self.supported_tickers):
            self.market_table.setItem(row, 0, QTableWidgetItem(ticker))
            self.market_table.setItem(row, 1, QTableWidgetItem("--"))
            self.market_table.setItem(row, 2, QTableWidgetItem("--"))
            self.market_table.setItem(row, 3, QTableWidgetItem("Waiting"))
            self.market_table.setItem(row, 4, QTableWidgetItem("Not checked"))

        self.market_table.cellClicked.connect(self.handle_market_row_click)

        layout.addLayout(top)
        layout.addWidget(self.market_table)

        return card

    def _create_customer_panel(self):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(330)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        card.setLayout(layout)

        if self.role == "agent":
            title = QLabel("Agent Customer List")
            title.setFont(QFont("Arial", 15, QFont.Weight.Bold))

            self.customer_table = QTableWidget()
            self.customer_table.setColumnCount(2)
            self.customer_table.setHorizontalHeaderLabels(["Customer", "Role"])
            self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.customer_table.setMinimumHeight(230)
            self.customer_table.cellClicked.connect(self.handle_customer_click)

            holdings_title = QLabel("Selected Customer Shares")
            holdings_title.setFont(QFont("Arial", 15, QFont.Weight.Bold))

            self.holdings_table = QTableWidget()
            self.holdings_table.setColumnCount(3)
            self.holdings_table.setHorizontalHeaderLabels(["Ticker", "Qty", "Avg Buy"])
            self.holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.holdings_table.setMinimumHeight(230)
            self.holdings_table.cellClicked.connect(self.handle_holding_click)

            layout.addWidget(title)
            layout.addWidget(self.customer_table)
            layout.addWidget(holdings_title)
            layout.addWidget(self.holdings_table)

            self.load_customers()

        else:
            title = QLabel("My Shares")
            title.setFont(QFont("Arial", 15, QFont.Weight.Bold))

            self.customer_table = None

            self.holdings_table = QTableWidget()
            self.holdings_table.setColumnCount(3)
            self.holdings_table.setHorizontalHeaderLabels(["Ticker", "Qty", "Avg Buy"])
            self.holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.holdings_table.setMinimumHeight(480)
            self.holdings_table.cellClicked.connect(self.handle_holding_click)

            layout.addWidget(title)
            layout.addWidget(self.holdings_table)

            self.load_customer_holdings(self.user["id"])

        return card

    def _create_main_panel(self):
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        card.setLayout(layout)

        control_row = QHBoxLayout()

        self.selected_stock_label = QLabel(f"Selected Stock: {self.selected_ticker}")
        self.selected_stock_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        self.range_dropdown = QComboBox()
        self.range_dropdown.addItems(["1 Week", "1 Month", "3 Months", "1 Year"])
        self.range_dropdown.setCurrentText("1 Year")
        self.range_dropdown.currentTextChanged.connect(self.update_range_from_dropdown)

        fetch_btn = QPushButton("Fetch Selected Stock")
        fetch_btn.clicked.connect(self.handle_fetch_data)

        predict_btn = QPushButton("Run Prediction")
        predict_btn.clicked.connect(self.handle_prediction)

        control_row.addWidget(self.selected_stock_label)
        control_row.addStretch()
        control_row.addWidget(QLabel("Range:"))
        control_row.addWidget(self.range_dropdown)
        control_row.addWidget(fetch_btn)
        control_row.addWidget(predict_btn)

        cards = QGridLayout()

        self.price_card = self._small_card("Current Price", "$ --")
        self.change_card = self._small_card("Market Change", "-- %")
        self.signal_card = self._small_card("Trend Signal", "Waiting")
        self.volume_card = self._small_card("Volume", "--")

        cards.addWidget(self.price_card, 0, 0)
        cards.addWidget(self.change_card, 0, 1)
        cards.addWidget(self.signal_card, 0, 2)
        cards.addWidget(self.volume_card, 0, 3)

        chart_and_prediction = QHBoxLayout()
        chart_and_prediction.setSpacing(14)

        chart_card = QFrame()
        chart_card.setObjectName("card")
        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(12, 12, 12, 12)
        chart_card.setLayout(chart_layout)

        chart_title = QLabel("Live Price Movement")
        chart_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        self.chart_widget = PriceChartWidget()
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.chart_widget)

        right_panel = QFrame()
        right_panel.setObjectName("card")
        right_panel.setMinimumWidth(340)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(12)
        right_panel.setLayout(right_layout)

        prediction_title = QLabel("Prediction Panel")
        prediction_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        self.prediction_chart = PredictionMiniChart()

        self.metrics_card = self._small_card("Model Metrics", "Not computed")
        self.alert_card = self._small_card("Alert Status", "No alert")

        self.recommendation_label = QLabel("Recommendation: Run prediction to generate guidance.")
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet(
            "background-color: #eff6ff; color: #1e3a8a; padding: 12px; border-radius: 8px;"
        )

        right_layout.addWidget(prediction_title)
        right_layout.addWidget(self.prediction_chart)
        right_layout.addWidget(self.metrics_card)
        right_layout.addWidget(self.alert_card)
        right_layout.addWidget(self.recommendation_label)
        right_layout.addStretch()

        chart_and_prediction.addWidget(chart_card, 3)
        chart_and_prediction.addWidget(right_panel, 1)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #374151;")

        layout.addLayout(control_row)
        layout.addLayout(cards)
        layout.addLayout(chart_and_prediction)
        layout.addWidget(self.status_label)

        return card

    def _small_card(self, title, value):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(90)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        card.setLayout(layout)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6b7280; font-size: 12px;")

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        value_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.value_label = value_label
        return card

    def update_range_from_dropdown(self):
        mapping = {
            "1 Week": "5d",
            "1 Month": "1mo",
            "3 Months": "3mo",
            "1 Year": "1y",
        }

        self.current_period = mapping.get(self.range_dropdown.currentText(), "1y")

    def load_customers(self):
        customers = self.holding_service.get_customers()
        self.customer_table.setRowCount(len(customers))

        for row, customer in enumerate(customers):
            name_item = QTableWidgetItem(customer["username"])
            name_item.setData(1000, customer["id"])

            self.customer_table.setItem(row, 0, name_item)
            self.customer_table.setItem(row, 1, QTableWidgetItem(customer["role"]))

    def handle_customer_click(self, row, column):
        item = self.customer_table.item(row, 0)
        if not item:
            return

        self.selected_customer_id = item.data(1000)
        self.load_customer_holdings(self.selected_customer_id)

    def load_customer_holdings(self, customer_id):
        holdings = self.holding_service.get_customer_holdings(customer_id)
        self.holdings_table.setRowCount(len(holdings))

        for row, holding in enumerate(holdings):
            self.holdings_table.setItem(row, 0, QTableWidgetItem(str(holding["ticker"])))
            self.holdings_table.setItem(row, 1, QTableWidgetItem(str(holding["quantity"])))
            self.holdings_table.setItem(
                row,
                2,
                QTableWidgetItem(f"${float(holding['average_buy_price']):.2f}")
            )

    def handle_holding_click(self, row, column):
        item = self.holdings_table.item(row, 0)
        if not item:
            return

        self.selected_ticker = item.text()
        self.selected_stock_label.setText(f"Selected Stock: {self.selected_ticker}")
        self.handle_fetch_data()

    def handle_market_row_click(self, row, column):
        item = self.market_table.item(row, 0)
        if not item:
            return

        self.selected_ticker = item.text()
        self.selected_stock_label.setText(f"Selected Stock: {self.selected_ticker}")
        self.handle_fetch_data()

    def refresh_market_watch(self):
        self.status_label.setText("Status: Refreshing market watch...")

        for row, ticker in enumerate(self.supported_tickers):
            try:
                df = fetch_stock_data(ticker, "5d")

                if df is None or df.empty or len(df) < 2:
                    continue

                close_col = "Close" if "Close" in df.columns else "close"

                latest = float(df.iloc[-1][close_col])
                previous = float(df.iloc[-2][close_col])
                change = ((latest - previous) / previous) * 100

                signal = "Bullish ▲" if change >= 0 else "Bearish ▼"
                status = "Alert" if abs(change) >= 2 else "Normal"

                self.market_table.setItem(row, 1, QTableWidgetItem(f"${latest:.2f}"))
                self.market_table.setItem(row, 2, QTableWidgetItem(f"{change:.2f}%"))
                self.market_table.setItem(row, 3, QTableWidgetItem(signal))
                self.market_table.setItem(row, 4, QTableWidgetItem(status))

            except Exception as e:
                print(f"Market refresh error for {ticker}: {e}")

        self.status_label.setText("Status: Market watch refreshed.")

    def handle_fetch_data(self):
        ticker = self.selected_ticker
        self.status_label.setText(f"Status: Fetching data for {ticker}...")

        self.raw_df = fetch_stock_data(ticker, self.current_period)

        if self.raw_df is None or self.raw_df.empty:
            QMessageBox.warning(self, "No Data", f"No stock data fetched for {ticker}.")
            self.status_label.setText("Status: Fetch failed.")
            return

        rows_inserted = load_stock_data(ticker, self.raw_df)
        self.featured_df = compute_features(self.raw_df)

        chart_df = (
            self.featured_df
            if self.featured_df is not None and not self.featured_df.empty
            else self.raw_df
        )

        self.chart_widget.update_chart(chart_df, ticker)

        close_col = "Close" if "Close" in self.raw_df.columns else "close"
        volume_col = "Volume" if "Volume" in self.raw_df.columns else "volume"

        latest = float(self.raw_df.iloc[-1][close_col])
        previous = float(self.raw_df.iloc[-2][close_col])
        change = ((latest - previous) / previous) * 100
        volume = int(self.raw_df.iloc[-1][volume_col])

        self.price_card.value_label.setText(f"${latest:.2f}")
        self.change_card.value_label.setText(f"{change:.2f}%")
        self.signal_card.value_label.setText("Bullish ▲" if change >= 0 else "Bearish ▼")
        self.volume_card.value_label.setText(f"{volume:,}")

        self.alert_card.value_label.setText("Alert" if abs(change) >= 2 else "Normal")

        self.status_label.setText(f"Status: Loaded {ticker}. Rows inserted: {rows_inserted}")

    def handle_prediction(self):
        if self.featured_df is None or self.featured_df.empty:
            QMessageBox.warning(
                self,
                "Missing Data",
                "Please fetch enough data first. Use 1 Year for best results."
            )
            return

        try:
            X_train, X_test, y_train, y_test = self.model_trainer.prepare_data(self.featured_df)
            model = self.model_trainer.train_linear_regression(X_train, y_train)
            metrics = self.model_trainer.evaluate_model(model, X_test, y_test)

            prediction_df = predict_future(
                self.featured_df,
                model,
                self.model_trainer.FEATURE_COLUMNS,
                days=7,
            )

            self.prediction_chart.update_prediction(prediction_df, self.selected_ticker)

            self.metrics_card.value_label.setText(
                f"MAE {metrics['MAE']} | RMSE {metrics['RMSE']} | R² {metrics['R2']}"
            )

            close_col = "Close" if "Close" in self.featured_df.columns else "close"

            current = float(self.featured_df.iloc[-1][close_col])
            previous = float(self.featured_df.iloc[-2][close_col])

            alerts = self.alert_service.check_price_change(self.selected_ticker, current, previous)

            if alerts:
                msg = alerts[0]["message"]
                self.alert_card.value_label.setText("Triggered")
                self.alert_service.notify_users_for_stock(
                    self.selected_ticker,
                    msg,
                    alerts[0]["percent_change"],
                )
            else:
                self.alert_card.value_label.setText("No Alert")

            profile = self._get_user_profile(self.user["id"])
            last_prediction = float(prediction_df["predicted_close"].iloc[-1])
            trend = "bullish" if last_prediction > current else "bearish"

            recommendation = RecommendationService.generate_recommendation(
                profile,
                prediction_df,
                trend,
            )

            self.recommendation_label.setText(f"Recommendation: {recommendation}")
            self.status_label.setText(f"Status: Prediction completed for {self.selected_ticker}.")

        except Exception as e:
            QMessageBox.critical(self, "Prediction Error", str(e))
            print(f"Prediction error: {e}")

    def handle_logout(self):
        confirm = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.controller.logout()

    def _get_user_profile(self, user_id):
        conn = get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM customer_profiles WHERE user_id = %s", (user_id,))
            return cursor.fetchone()

        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None

        finally:
            cursor.close()
            conn.close()