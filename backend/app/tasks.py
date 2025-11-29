from .celery_stub import celery_app
from .models import Appointment, Treatment, Doctor, Patient, ExportJob
from . import db, mail
from .config import Config
from flask_mail import Message
from datetime import date
import requests, pandas as pd, os, csv

@celery_app.task
def daily_reminder_task():
    today = date.today()
    appts = Appointment.query.filter_by(date=today, status='Booked').all()
    
    if not appts:
        print("No booked appointments for today.")
        return

    print(f"Found {len(appts)} appointments for today. Sending email reminders...")
    
    for a in appts:
        if not a.patient.user.email:
            print(f"Skipping Appointment ID {a.id}: Patient has no email.")
            continue

        msg = Message("Appointment Reminder", recipients=[a.patient.user.email])
        msg.body = (
            f"Hello {a.patient.user.username},\n\n"
            f"You have an appointment scheduled for today ({today.isoformat()}) at {a.time.strftime('%H:%M')}.\n"
            f"Doctor: Dr. {a.doctor.user.username}\n\n"
            f"Please arrive on time.\n"
            f"HMS Team"
        )
        
        try:
            mail.send(msg)
            print(f"Sent email reminder to {a.patient.user.email} for Appointment ID {a.id}")
        except Exception as e:
            print(f"Error sending email to {a.patient.user.email}: {e}")

@celery_app.task
def monthly_report_task(doctor_id, year=None, month=None):
    from datetime import datetime
    if not year or not month:
        today = datetime.today()
        # Default to previous month
        if today.month == 1:
            month = 12; year = today.year - 1
        else:
            month = today.month - 1; year = today.year
            
    doc = Doctor.query.get(doctor_id)
    if not doc: return
    
    import calendar
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    
    appts = Appointment.query.filter(
        Appointment.doctor_id==doctor_id, 
        Appointment.status=='Completed',
        Appointment.date >= start_date,
        Appointment.date <= end_date
    ).all()
    
    rows = []
    for a in appts:
        t = a.treatment
        rows.append({
            'Appointment ID': a.id, 
            'Patient': a.patient.user.username, 
            'Date': a.date.isoformat(), 
            'Time': a.time.strftime('%H:%M'),
            'Diagnosis': t.diagnosis if t else '', 
            'Prescription': t.prescription if t else ''
        })
        
    df = pd.DataFrame(rows)
    
    report_filename = f'monthly_report_doctor_{doctor_id}_{year}_{month}.html'
    report_path = os.path.join(Config.EXPORT_PATH, report_filename)
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            h1 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h1>Monthly Activity Report</h1>
        <p><strong>Doctor:</strong> Dr. {doc.user.username}</p>
        <p><strong>Period:</strong> {month}/{year}</p>
        <p><strong>Total Appointments:</strong> {len(appts)}</p>
        <hr>
        {df.to_html(index=False, classes='table') if not df.empty else '<p>No completed appointments found for this period.</p>'}
    </body>
    </html>
    """
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    webhook = Config.GOOGLE_CHAT_WEBHOOK
    if webhook:
        try:
            msg_text = f"📊 *Monthly Report Ready*\nReport for Dr. {doc.user.username} ({month}/{year}) has been generated.\nPath: `{report_path}`"
            requests.post(webhook, json={'text': msg_text})
        except Exception as e:
            print('webhook err', e)
            
    return report_path

@celery_app.task
def export_treatments_task(job_id):
    job = ExportJob.query.get(job_id)
    if not job: return
    
    # Eager load relationships to avoid N+1
    # But for simplicity in this task, we'll just access them (SQLAlchemy will lazy load)
    treatments = db.session.query(Treatment).filter(Treatment.patient_id==job.patient_id).all()
    
    rows = []
    for tr in treatments:
        # specific fields requested
        doc_name = tr.appointment.doctor.user.username if tr.appointment and tr.appointment.doctor else 'Unknown'
        appt_date = tr.appointment.date.isoformat() if tr.appointment else ''
        
        rows.append({
            'User ID': tr.patient.user.id,
            'Username': tr.patient.user.username,
            'Consulting Doctor': doc_name,
            'Appointment Date': appt_date,
            'Diagnosis': tr.diagnosis,
            'Treatment': tr.prescription,
            'Next Visit': tr.notes # Mapping notes to Next Visit as per plan
        })
        
    path = os.path.join(Config.EXPORT_PATH, f'export_treatments_patient_{job.patient_id}_{job.id}.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['User ID', 'Username', 'Consulting Doctor', 'Appointment Date', 'Diagnosis', 'Treatment', 'Next Visit']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    job.status = 'done'; job.path = path; db.session.commit()
    
    # Send email notification
    patient = Patient.query.get(job.patient_id)
    patient_email = patient.user.email if patient and patient.user else None
    if patient_email:
        try:
            msg = Message("Export Ready", recipients=[patient_email])
            msg.body = f"Hello,\n\nYour treatment history export is ready.\nFile: {path}\n\nHMS Team"
            mail.send(msg)
            print(f"Sent export notification to {patient_email}")
        except Exception as e:
            print(f"Error sending export email: {e}")
            
    return path
