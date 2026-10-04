import argparse
from datetime import datetime, timedelta

from labs.lab02.task1 import *


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lab2.lab02.main")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "demo":
        standard_account = UserAccount("User", "email@gmail.com", "guest", True)
        admin = UserAccount("Admin", "email3@gmail.com", "admin", True)
        admin.user = Admin("Admin", "email3@gmail.com", True, None)

        standard_account.user.set_password("password1")
        admin.user.set_password("password4")

        print(f"""
Створено 2 облікові записи:
{standard_account.user}
{admin.user}
""")

        standard_account.login("User", "password1", "192.168.153.2")
        print(
            f"Результат спроби входу з правильним паролем: {'Success' if standard_account.is_authenticated() else 'failure'}"
        )
        standard_account.logout()
        standard_account.login("User", "wrongpass", "192.168.153.2")
        print(
            f"Результат спроби входу з неправильним паролем: {'Success' if standard_account.is_authenticated() else 'failure'}"
        )
        standard_account.login("User", "password1", "192.168.153.2")

        print(f"""
Email користувача User до зміни: {standard_account.user.email}
""")
        standard_account.user.email = "newemail@gmail.com"
        print(f"Email кориcтувача User після зміни: {standard_account.user.email}\n\n")
        print("Результат встановити Email неправильного формату:")
        try:
            standard_account.user.email = "bademail"
            print("Зміна відбулась успішно! Новий email: bademail")
        except ValueError as e:
            print("Помилка", e)

        print(
            f"Стан автентифікації User: {'authenticated' if standard_account.is_authenticated() else 'not authenticated'}"
        )
        standard_account.logout()
        print("Здійснено вихід з облікового запису")
        print(
            f"Стан автентифікації User: {'authenticated' if standard_account.is_authenticated() else 'not authenticated'}"
        )

        standard_account.login("User", "password1", "192.168.153.2")
        print("Здійснено вхід в обліковий запис User")
        print("Штучно встановлено останній час активності на 30 хвилин тому")
        standard_account.session.last_activity = datetime.now(timezone.utc) - timedelta(
            minutes=30
        )

        print(
            "Перевірка стану автентифікації User:",
            "authenticated"
            if standard_account.is_authenticated()
            else "not authenticated",
        )

        print("Audit Log:")
        print("\t- User:")
        standard_account.auditlog.show_all()
        print("\t- Admin:")
        admin.auditlog.show_all()

        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
