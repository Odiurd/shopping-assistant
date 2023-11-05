from datetime import datetime
from settings.config import (
    DATABASE_FILE,
    EMAIL_STYLE,
)
from settings.personal_config import FROM_EMAIL, TO_EMAIL
from database.database_manager import DatabaseManager
from notifiers.email_notifier import EmailNotifier


def send_shopping_notification():
    db_manager = DatabaseManager(DATABASE_FILE)
    discounted_items = db_manager.get_discounted_items_today()

    notifier = EmailNotifier()
    subject = f"Shopping notifications {datetime.utcnow().strftime('%Y-%m-%d')}"
    email_content = notifier.build_email_content(
        email_style=EMAIL_STYLE, discounted_items_dict=discounted_items
    )
    notifier.send_email(
        from_email=FROM_EMAIL,
        to_email=TO_EMAIL,
        subject=subject,
        content=email_content,
        content_type=EMAIL_STYLE,
    )


if __name__ == "__main__":
    send_shopping_notification()
    print(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - email sent")
