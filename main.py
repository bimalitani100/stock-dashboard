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
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_commands = f.read()

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


def main():
    initialize_database()
    run_schema()

    auth_service = AuthService()
    auth_service.create_default_users()

    app = QApplication(sys.argv)

    windows = {}

    def handle_login_success(user):
        windows["main_window"] = MainWindow(user)
        windows["main_window"].show()

    windows["login_window"] = LoginWindow(handle_login_success)
    windows["login_window"].show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()