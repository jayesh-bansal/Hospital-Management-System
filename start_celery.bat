@echo off
echo Starting Celery Worker and Beat...
cd backend
if not exist venv (
    echo Virtual environment not found! Please run start_app.bat first to set it up.
    pause
    exit
)
call venv\Scripts\activate

:: Start Worker (using pool=solo for Windows compatibility)
start "Celery Worker" cmd /k "celery -A app.celery_stub.celery_app worker --loglevel=info --pool=solo"

:: Start Beat (Scheduler)
start "Celery Beat" cmd /k "celery -A app.celery_stub.celery_app beat --loglevel=info"

echo Celery started in new windows.
