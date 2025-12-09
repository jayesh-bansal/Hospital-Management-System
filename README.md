# Hospital Management System

A comprehensive web-based application for managing hospital operations, including patient appointments, doctor schedules, medical records, and administrative tasks.

## Features

- **Role-Based Access**: Distinct portals for Admins, Doctors, and Patients.
- **Appointment Booking**: Patients can book, reschedule, and cancel appointments.
- **Doctor Availability**: Flexible scheduling for doctors.
- **Medical Records**: Digital diagnosis and prescription management.
- **Automated Reminders**: Daily email reminders for upcoming appointments.
- **Reporting**: Monthly activity reports for doctors and treatment history exports for patients.

## Tech Stack

- **Backend**: Flask (Python), SQLAlchemy, Celery, Redis
- **Frontend**: Vue.js 3, Bootstrap 5
- **Database**: SQLite (default) / PostgreSQL compatible

## Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server (for background tasks)

## Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/jayesh-bansal/Hospital-Management-System.git
    cd Hospital_Management_System
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    # source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    ```

## Running the Application

### Quick Start (Windows)
Use the provided batch scripts in the root directory:
1.  Start Redis Server manually.
2.  Run `start_app.bat` to launch both Backend and Frontend.
3.  Run `start_celery.bat` to start the background task worker.

### Manual Start

**Backend:**
```bash
cd backend
# Activate venv
python app.py
```

**Frontend:**
```bash
cd frontend
npm run serve
```

**Celery Worker:**
```bash
cd backend
# Activate venv
celery -A app.celery_stub.celery_app worker --loglevel=info --pool=solo
```

## Documentation

- **Project Details**: See [project_details.md](project_details.md) for architecture and schema info.
- **API Specification**: See [openapi.yaml](openapi.yaml) for detailed API endpoints.
