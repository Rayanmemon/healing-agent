@echo off
echo ============================================
echo    Starting Healing Agent...
echo ============================================

:: Start backend
cd /d "%~dp0backend"
start "Backend" cmd /k "python app.py"

:: Wait a moment
timeout /t 2 /nobreak > nul

:: Start frontend
cd /d "%~dp0frontend"
start "Frontend" cmd /k "npm run dev"

echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo (Close this window when done)
pause
