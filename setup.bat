@echo off
REM Quick setup script for Windows
REM This creates a virtual environment and installs dependencies

echo.
echo ===============================================
echo  UV Oil Leak Detection - Local Setup
echo ===============================================
echo.

REM Navigate to backend directory
cd /d "%~dp0"

REM Create virtual environment
echo [1/4] Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [3/4] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Done
echo.
echo [4/4] Setup complete!
echo.
echo To run the server, use:
echo   venv\Scripts\activate.bat
echo   python app.py
echo.
echo API will be available at:
echo   http://localhost:5000
echo.
