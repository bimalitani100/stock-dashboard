from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PriceChartWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure(figsize=(9, 5))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_chart(self, df, ticker="Stock"):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if df is None or df.empty:
            ax.set_title("No chart data available")
            self.canvas.draw()
            return

        x_values = df["Date"] if "Date" in df.columns else df.index
        close_col = "Close" if "Close" in df.columns else "close"

        current = float(df.iloc[-1][close_col])
        previous = float(df.iloc[-2][close_col]) if len(df) > 1 else current
        change = ((current - previous) / previous) * 100 if previous else 0

        ax.plot(x_values, df[close_col], linewidth=2.5, label="Live Price")

        if "ma_20" in df.columns:
            ax.plot(x_values, df["ma_20"], linewidth=1.5, linestyle="--", label="MA 20")

        if "ma_50" in df.columns:
            ax.plot(x_values, df["ma_50"], linewidth=1.5, linestyle="--", label="MA 50")

        direction = "▲" if change >= 0 else "▼"
        ax.set_title(f"{ticker}  ${current:.2f}  {direction} {change:.2f}%")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price ($)")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper left")
        self.figure.autofmt_xdate()
        self.canvas.draw()


class PredictionMiniChart(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure(figsize=(4, 2.7))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_prediction(self, prediction_df, ticker="Stock"):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if prediction_df is None or prediction_df.empty:
            ax.set_title("No prediction yet")
            self.canvas.draw()
            return

        ax.plot(
            prediction_df["day"],
            prediction_df["predicted_close"],
            marker="o",
            linewidth=2,
            label="Forecast"
        )

        ax.set_title(f"{ticker} 7-Day Forecast")
        ax.set_xlabel("Day")
        ax.set_ylabel("Predicted Price")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper left")
        self.canvas.draw()