@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (echo Python was not found. Install Python 3.10+ and enable Add Python to PATH.&pause&exit /b 1)
cd backend
python -m pip install -r requirements.txt
if errorlevel 1 (echo Dependency installation failed.&pause&exit /b 1)
python -m uvicorn app:app --host 127.0.0.1 --port 8000
pause
