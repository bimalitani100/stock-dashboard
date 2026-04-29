from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFrame,
)

from auth.auth_service import AuthService


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()

        self.on_login_success = on_login_success
        self.auth_service = AuthService()
        self.selected_role = None

        self.setWindowTitle("Stock Dashboard Login")
        self.setGeometry(420, 180, 520, 430)

        self.setStyleSheet("""
            QWidget {
                background-color: #eef2f7;
            }

            QLabel {
                color: #111827;
            }

            QFrame#loginCard {
                background-color: white;
                border-radius: 18px;
                border: 1px solid #dbe2ea;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                padding: 12px;
                font-size: 15px;
            }

            QLineEdit:focus {
                border: 2px solid #2563eb;
            }
        """)

        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(35, 35, 35, 35)
        self.setLayout(outer_layout)

        card = QFrame()
        card.setObjectName("loginCard")

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 28, 30, 28)
        card_layout.setSpacing(14)
        card.setLayout(card_layout)

        title = QLabel("Stock Dashboard Login")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))

        subtitle = QLabel("Choose your role and sign in to continue.")
        subtitle.setStyleSheet("color: #6b7280; font-size: 13px;")

        role_label = QLabel("Select Role")
        role_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        role_layout = QHBoxLayout()

        self.agent_button = QPushButton("Agent")
        self.customer_button = QPushButton("Customer")

        self.agent_button.clicked.connect(lambda: self.select_role("agent"))
        self.customer_button.clicked.connect(lambda: self.select_role("customer"))

        role_layout.addWidget(self.agent_button)
        role_layout.addWidget(self.customer_button)

        self.selected_role_label = QLabel("No role selected")
        self.selected_role_label.setStyleSheet("color: #6b7280; font-size: 12px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.hint_label = QLabel("Agent demo: agent / agent123")
        self.hint_label.setStyleSheet("color: #6b7280; font-size: 12px;")

        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        login_button.clicked.connect(self.handle_login)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(role_label)
        card_layout.addLayout(role_layout)
        card_layout.addWidget(self.selected_role_label)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.hint_label)
        card_layout.addSpacing(8)
        card_layout.addWidget(login_button)

        outer_layout.addWidget(card)

        self.select_role("agent")

    def select_role(self, role):
        self.selected_role = role

        if role == "agent":
            self.agent_button.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                }
            """)
            self.customer_button.setStyleSheet("""
                QPushButton {
                    background-color: #e5e7eb;
                    color: #111827;
                }
            """)

            self.selected_role_label.setText("Selected Role: Agent")
            self.username_input.setText("agent")
            self.password_input.setText("")
            self.hint_label.setText("Agent demo login: agent / agent123")

        else:
            self.customer_button.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                }
            """)
            self.agent_button.setStyleSheet("""
                QPushButton {
                    background-color: #e5e7eb;
                    color: #111827;
                }
            """)

            self.selected_role_label.setText("Selected Role: Customer")
            self.username_input.setText("customer1")
            self.password_input.setText("")
            self.hint_label.setText("Customer demo login: customer1 / cust1123")

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not self.selected_role:
            QMessageBox.warning(self, "Missing Role", "Please select Agent or Customer.")
            return

        if not username or not password:
            QMessageBox.warning(self, "Missing Info", "Please enter username and password.")
            return

        user = self.auth_service.authenticate_user(username, password)

        if not user:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            return

        if user["role"] != self.selected_role:
            QMessageBox.warning(
                self,
                "Wrong Role",
                f"This account is not a {self.selected_role}. Please select the correct role."
            )
            return

        self.on_login_success(user)
        self.close()