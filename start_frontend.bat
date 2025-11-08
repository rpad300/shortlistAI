@echo off
REM Script to start the frontend dev server
REM Run from project root

echo ========================================
echo Starting ShortlistAI Frontend
echo ========================================
echo.

cd src\frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    echo.
)

REM Start dev server
echo Starting Vite dev server...
echo App will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

