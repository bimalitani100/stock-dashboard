from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
)

from auth.auth_service import AuthService


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.auth_service = AuthService()

        self.setWindowTitle("Login")
        self.setGeometry(300, 200, 350, 220)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Stock Dashboard Login")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)

        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return

        user = self.auth_service.authenticate_user(username, password)

        if user:
            self.on_login_success(user)
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")