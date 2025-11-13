@echo off
REM SEO Validation Script for Windows
REM Validates structured data and SEO metadata

echo SEO Validation for ShortlistAI
echo ================================
echo.

python scripts\validate_seo.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Validation completed successfully!
) else (
    echo.
    echo Validation found some issues. Please review the output above.
)

pause

