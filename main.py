import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from auth.auth_service import AuthService
from auth.login_window import LoginWindow
from config.db_config import initialize_database, get_connection
from dashboard.main_window import MainWindow


def run_schema():
    base_dir = Path(__file__).resolve().parent
    schema_path = base_dir / "config" / "schema.sql"

    conn = get_connection()
    if conn is None:
        print("Could not connect to MySQL to run schema.")
        return

    try:
        cursor = conn.cursor()

        with open(schema_path, "r", encoding="utf-8") as file:
            sql_commands = file.read()

        for statement in sql_commands.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)

        conn.commit()
        print("Schema loaded successfully.")

    except Exception as e:
        conn.rollback()
        print(f"Error running schema: {e}")

    finally:
        cursor.close()
        conn.close()


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.main_window = None

        initialize_database()
        run_schema()

        self.auth_service = AuthService()
        self.auth_service.create_default_users()

    def show_login(self):
        self.login_window = LoginWindow(self.handle_login_success)
        self.login_window.show()

    def handle_login_success(self, user):
        self.main_window = MainWindow(user, self)
        self.main_window.show()

        if self.login_window:
            self.login_window.close()

    def logout(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.show_login()

    def run(self):
        self.show_login()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    controller = AppController()
    controller.run()