@echo off
echo ========================================
echo   ISAVS Development Server Starter
echo ========================================
echo.
echo Starting Backend (Port 8000)...
start cmd /k "cd backend && uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak > nul
echo.
echo Starting Frontend (Port 3001)...
start cmd /k "cd frontend && npm run dev"
echo.
echo ========================================
echo   Servers Starting...
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3001
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause > nul
