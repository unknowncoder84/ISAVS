@echo off
echo ========================================
echo ISAVS 2026 - Dual Portal System
echo ========================================
echo Starting Backend (Port 6000)...
echo Starting Teacher Dashboard (Port 2001)...
echo Starting Student Kiosk (Port 2002)...
echo ========================================
echo.

start "ISAVS Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 6000"
timeout /t 3 /nobreak >nul

start "Teacher Dashboard" cmd /k "cd frontend && npm run dev:teacher"
timeout /t 2 /nobreak >nul

start "Student Kiosk" cmd /k "cd frontend && npm run dev:student"

echo.
echo ========================================
echo All services started!
echo ========================================
echo Backend:   http://localhost:6000
echo Teacher:   http://localhost:2001
echo Student:   http://localhost:2002
echo ========================================
echo.
echo Press any key to exit...
pause >nul
