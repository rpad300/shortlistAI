@echo off
REM ShortlistAI - Script de Início Único
REM Inicia Backend e Frontend

echo.
echo ========================================
echo   INICIANDO SHORTLISTAI
echo ========================================
echo.

REM Matar processos antigos
echo Encerrando processos antigos...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo OK - Processos antigos encerrados
echo.

REM Iniciar Backend em nova janela
echo Iniciando Backend...
start "ShortlistAI Backend" cmd /k "cd src\backend && .\venv\Scripts\activate && python main.py"
echo OK - Backend a iniciar...
echo.

REM Aguardar backend
timeout /t 5 /nobreak >nul

REM Iniciar Frontend em nova janela
echo Iniciando Frontend...
start "ShortlistAI Frontend" cmd /k "cd src\frontend && npm run dev"
echo OK - Frontend a iniciar...
echo.

REM Aguardar frontend
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo   SHORTLISTAI INICIADO!
echo ========================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/api/docs
echo.
echo ========================================
echo.
echo ABRE NO BROWSER:
echo   http://localhost:3000
echo.
echo Para parar:
echo   Fecha as janelas do Backend e Frontend
echo.
pause

