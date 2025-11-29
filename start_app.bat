@echo off
echo Starting HMS...

:: Check and Setup Backend
if not exist "backend\venv" (
    echo Backend venv not found. Setting up...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
)

:: Start Backend
start "HMS Backend" cmd /k "cd backend && venv\Scripts\activate && python app.py"

:: Check and Setup Frontend
if not exist "frontend\node_modules" (
    echo Frontend node_modules not found. Installing dependencies...
    cd frontend
    call npm install
    cd ..
)

:: Start Frontend
start "HMS Frontend" cmd /k "cd frontend && npm run serve"

echo Both servers are starting in separate windows.
echo Backend: http://127.0.0.1:5000
echo Frontend: http://localhost:8080
