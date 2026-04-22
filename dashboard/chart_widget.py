from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PriceChartWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_chart(self, df):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if df is None or df.empty:
            ax.set_title("No data available")
            self.canvas.draw()
            return

        # Use actual column values, not the column name string
        if "Date" in df.columns:
            x_values = df["Date"]
        else:
            x_values = df.index

        close_col = "Close" if "Close" in df.columns else "close"

        ax.plot(x_values, df[close_col], label="Close Price")

        if "ma_20" in df.columns:
            ax.plot(x_values, df["ma_20"], label="MA 20")

        if "ma_50" in df.columns:
            ax.plot(x_values, df["ma_50"], label="MA 50")

        ax.set_title("Stock Price History")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        self.figure.autofmt_xdate()
        self.canvas.draw()

    def show_predictions(self, actual_df, prediction_df):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if actual_df is not None and not actual_df.empty:
            if "Date" in actual_df.columns:
                x_values = actual_df["Date"]
            else:
                x_values = actual_df.index

            close_col = "Close" if "Close" in actual_df.columns else "close"
            ax.plot(x_values, actual_df[close_col], label="Actual Close")

        if prediction_df is not None and not prediction_df.empty:
            ax.plot(
                prediction_df["day"],
                prediction_df["predicted_close"],
                label="Predicted",
                linestyle="--",
            )

        ax.set_title("Actual vs Predicted")
        ax.legend()
        self.canvas.draw()