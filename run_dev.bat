@echo off
echo Starting Backend...
start "Flask Backend" cmd /k "python app.py"

echo Starting Frontend...
cd frontend
start "React Frontend" cmd /k "npm run dev"

echo.
echo App should be running at: http://localhost:5173
pause
