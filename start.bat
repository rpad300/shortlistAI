@echo off
setlocal

REM Caminho raiz do repositório (mesma pasta deste script)
cd /d "%~dp0"

REM Executa o launcher PowerShell numa única consola
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"

endlocal
