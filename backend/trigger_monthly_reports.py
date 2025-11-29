from app import create_app, db
from app.models import Doctor
from app.tasks import monthly_report_task
from datetime import date

app = create_app()

def trigger_reports():
    with app.app_context():
        print("Triggering monthly reports for all doctors...")
        
        # Determine previous month
        today = date.today()
        if today.month == 1:
            month = 12; year = today.year - 1
        else:
            month = today.month - 1; year = today.year
            
        print(f"Generating reports for period: {month}/{year}")
        
        doctors = Doctor.query.all()
        for doc in doctors:
            print(f" - Triggering for Dr. {doc.user.username} (ID: {doc.id})")
            monthly_report_task(doc.id, year, month)
            
        print(f"Done. Triggered for {len(doctors)} doctors.")

if __name__ == '__main__':
    trigger_reports()
