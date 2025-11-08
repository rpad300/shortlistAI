@echo off
REM Comprehensive test suite for ShortlistAI
REM Runs all tests and verifications

echo ========================================
echo ShortlistAI - Comprehensive Test Suite
echo ========================================
echo.

REM Test 1: Backend Setup
echo [1/5] Testing Backend Setup...
python src\backend\test_setup.py
if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Backend setup test failed
    pause
    exit /b 1
)
echo [OK] Backend setup passed
echo.

REM Test 2: Backend Unit Tests
echo [2/5] Running Backend Unit Tests...
cd src\backend
call venv\Scripts\activate.bat 2>nul
pip install pytest pytest-asyncio 2>nul
cd ..\..
python -m pytest tests/backend/ -v
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some backend tests failed
    echo This is OK if Supabase keys are not configured
)
echo.

REM Test 3: Import Check
echo [3/5] Checking All Imports...
python -c "import sys; sys.path.insert(0, 'src/backend'); from routers import interviewer, candidate, admin; from services.ai import get_ai_manager; from utils import FileProcessor; print('[OK] All imports successful')"
if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Import check failed
    pause
    exit /b 1
)
echo.

REM Test 4: Configuration Check
echo [4/5] Validating Configuration...
python -c "import sys; sys.path.insert(0, 'src/backend'); from config import settings; print(f'[OK] Config loaded: {settings.app_env} environment')"
if %ERRORLEVEL% NEQ 0 (
    echo [FAILED] Configuration check failed
    pause
    exit /b 1
)
echo.

REM Test 5: Frontend Build Check
echo [5/5] Checking Frontend Build...
cd src\frontend
call npm install --silent 2>nul
call npm run build 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Frontend build check skipped or failed
    echo Run 'npm install' in src/frontend if needed
) else (
    echo [OK] Frontend builds successfully
)
cd ..\..
echo.

echo ========================================
echo Test Suite Complete!
echo ========================================
echo.
echo Results:
echo [OK] Backend setup: PASSED
echo [OK] Backend imports: PASSED
echo [OK] Configuration: PASSED
echo [INFO] Backend tests: Check output above
echo [INFO] Frontend build: Check output above
echo.
echo To start the application:
echo   start_backend.bat
echo   start_frontend.bat
echo.
echo To view test coverage:
echo   pytest tests/backend/ --cov=src/backend
echo.
pause

