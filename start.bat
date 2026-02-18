@echo off
REM eKYC System Quick Start Script for Windows
REM This script initializes and starts the complete eKYC system

echo.
echo ========================================
echo   eKYC Digital Banking System
echo ========================================
echo.

REM Step 1: Initialize Database
echo [1/3] Initializing Database...
cd backend
python scripts\init_db.py
if %errorlevel% neq 0 (
    echo ERROR: Database initialization failed
    pause
    exit /b 1
)
echo SUCCESS: Database initialized
echo.

REM Step 2: Start Backend
echo [2/3] Starting Backend Server...
echo Backend will run on http://process.env.NEXT_PUBLIC_API_URL
start "eKYC Backend" cmd /k "python main.py"
timeout /t 3 /nobreak >nul
echo SUCCESS: Backend started
echo.

REM Step 3: Start Frontend
echo [3/3] Starting Frontend Server...
cd ..\frontend
echo Frontend will run on http://localhost:3000
start "eKYC Frontend" cmd /k "npm run dev"
echo SUCCESS: Frontend started
echo.

echo ========================================
echo   System is now running!
echo ========================================
echo.
echo Frontend:  http://localhost:3000
echo Backend:   http://process.env.NEXT_PUBLIC_API_URL
echo API Docs:  http://process.env.NEXT_PUBLIC_API_URL/docs
echo.
echo Press any key to open the frontend in your browser...
pause >nul
start http://localhost:3000
