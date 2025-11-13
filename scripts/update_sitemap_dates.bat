@echo off
REM Sitemap Date Updater for Windows
REM Updates lastmod dates in sitemap.xml

echo Sitemap Date Updater
echo =====================
echo.

python scripts\update_sitemap_dates.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Sitemap dates updated successfully!
) else (
    echo.
    echo Failed to update sitemap dates. Please check the error above.
)

pause

