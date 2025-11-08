@echo off
REM Script to start the backend server
REM Run from project root

echo ========================================
echo Starting ShortlistAI Backend
echo ========================================
echo.

cd src\backend

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Checking dependencies...
pip install -q -r requirements.txt
echo.

REM Run test
echo Running setup test...
python test_setup.py
echo.

REM Start server
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/api/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

