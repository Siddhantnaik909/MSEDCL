@echo off
setlocal
title MSEDCL Quality Audit Portal
color 0A
cd /d "%~dp0"
if errorlevel 1 goto :error

set "PROJECT_DIR=%CD%"
set "PYTHON=%PROJECT_DIR%\.venv\Scripts\python.exe"

echo ============================================================
echo          MSEDCL Quality Audit Portal - Local Setup
echo ============================================================
echo.

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js is required to run the React frontend.
    echo Install Node.js LTS from https://nodejs.org, then run this file again.
    goto :error
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm was not found. Reinstall Node.js LTS and try again.
    goto :error
)

if not exist "%PYTHON%" (
    where py >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python 3 is required. Install Python and enable the Python launcher.
        goto :error
    )
    echo [*] Creating Python virtual environment...
    py -3 -m venv "%PROJECT_DIR%\.venv"
    if errorlevel 1 goto :error
)

"%PYTHON%" -c "import flask, pandas, openpyxl, werkzeug" >nul 2>nul
if errorlevel 1 (
    echo [*] Installing Python dependencies...
    "%PYTHON%" -m pip install -r "%PROJECT_DIR%\requirements.txt"
    if errorlevel 1 goto :error
)

if not exist "%PROJECT_DIR%\.env" if exist "%PROJECT_DIR%\.env.example" (
    echo [*] Creating local .env from .env.example...
    copy "%PROJECT_DIR%\.env.example" "%PROJECT_DIR%\.env" >nul
    if errorlevel 1 goto :error
)

if not exist "%PROJECT_DIR%\frontend\node_modules\vite\bin\vite.js" (
    echo [*] Installing React frontend dependencies...
    pushd "%PROJECT_DIR%\frontend"
    call npm.cmd ci
    if errorlevel 1 (
        popd
        goto :error
    )
    popd
)

echo [*] Initializing the database and applying migrations...
"%PYTHON%" -c "from config.settings import settings; from init_db import init_db; from migrate_db import run_migrations; init_db(settings.database_path); run_migrations(settings.database_path)"
if errorlevel 1 goto :error

echo.
echo [*] Starting Flask API at http://127.0.0.1:5000 ...
start "MSEDCL Flask API" cmd /k "cd /d ""%PROJECT_DIR%"" && ""%PYTHON%"" app.py"

echo [*] Starting React frontend at http://127.0.0.1:5173 ...
start "MSEDCL React UI" cmd /k "cd /d ""%PROJECT_DIR%\frontend"" && npm.cmd run dev -- --host 127.0.0.1 --port 5173 --strictPort"

echo [*] Opening the React sign-in page...
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5173/login"

echo.
echo React UI:  http://127.0.0.1:5173/login
echo Flask app: http://127.0.0.1:5000
echo Close both server windows to stop the application.
echo.
pause
exit /b 0

:error
echo.
echo [ERROR] Setup could not be completed. Review the message above.
pause
exit /b 1
