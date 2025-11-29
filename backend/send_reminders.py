from dotenv import load_dotenv
load_dotenv(override=True)

from app import create_app
from app.tasks import daily_reminder_task

app = create_app()

def send_reminders():
    with app.app_context():
        print(f"Config: Server={app.config['MAIL_SERVER']}, Port={app.config['MAIL_PORT']}, SSL={app.config['MAIL_USE_SSL']}")
        print("Triggering daily reminders...")
        daily_reminder_task()
        print("Done.")

if __name__ == '__main__':
    send_reminders()
