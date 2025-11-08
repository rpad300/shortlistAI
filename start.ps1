# ShortlistAI - Script de Início Único
# Inicia Backend e Frontend em paralelo

Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                ║" -ForegroundColor Cyan
Write-Host "║        🚀 INICIANDO SHORTLISTAI 🚀             ║" -ForegroundColor Green
Write-Host "║                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Matar processos antigos
Write-Host "🔄 Encerrando processos antigos..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null | Out-Null
taskkill /F /IM node.exe 2>$null | Out-Null
Start-Sleep -Seconds 2
Write-Host "✅ Processos antigos encerrados" -ForegroundColor Green
Write-Host ""

# Iniciar Backend
Write-Host "🐍 Iniciando Backend (Python + FastAPI)..." -ForegroundColor Cyan
$backendPath = "src\backend"
$backendScript = {
    param($path)
    Set-Location $path
    .\venv\Scripts\activate
    Write-Host "✅ Backend iniciado em http://localhost:8000" -ForegroundColor Green
    python main.py
}

$backendJob = Start-Job -ScriptBlock $backendScript -ArgumentList (Resolve-Path $backendPath)
Write-Host "✅ Backend a iniciar (Job ID: $($backendJob.Id))" -ForegroundColor Green
Write-Host ""

# Aguardar backend iniciar
Write-Host "⏳ Aguardando backend iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Iniciar Frontend
Write-Host "⚛️  Iniciando Frontend (React + Vite)..." -ForegroundColor Cyan
$frontendPath = "src\frontend"
$frontendScript = {
    param($path)
    Set-Location $path
    Write-Host "✅ Frontend iniciado em http://localhost:3000" -ForegroundColor Green
    npm run dev
}

$frontendJob = Start-Job -ScriptBlock $frontendScript -ArgumentList (Resolve-Path $frontendPath)
Write-Host "✅ Frontend a iniciar (Job ID: $($frontendJob.Id))" -ForegroundColor Green
Write-Host ""

# Aguardar servidores iniciarem
Write-Host "⏳ Aguardando servidores iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Verificar se estão a correr
Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                ║" -ForegroundColor Green
Write-Host "║        ✅ SHORTLISTAI INICIADO! ✅              ║" -ForegroundColor Yellow
Write-Host "║                                                ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                ║" -ForegroundColor Green
Write-Host "║  Backend:  http://localhost:8000               ║" -ForegroundColor White
Write-Host "║  Frontend: http://localhost:3000               ║" -ForegroundColor White
Write-Host "║  API Docs: http://localhost:8000/api/docs      ║" -ForegroundColor White
Write-Host "║                                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📱 ABRE NO BROWSER:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 Para parar os servidores:" -ForegroundColor Yellow
Write-Host "   Ctrl+C neste terminal" -ForegroundColor White
Write-Host ""
Write-Host "📊 Logs dos servidores:" -ForegroundColor Yellow
Write-Host "   Backend Job ID:  $($backendJob.Id)" -ForegroundColor White
Write-Host "   Frontend Job ID: $($frontendJob.Id)" -ForegroundColor White
Write-Host ""
Write-Host "Ver logs: Receive-Job -Id <JobID> -Keep" -ForegroundColor Gray
Write-Host ""

# Manter script aberto e mostrar logs
Write-Host "Carrega Ctrl+C para parar ambos os servidores..." -ForegroundColor Yellow
Write-Host ""

try {
    # Manter script vivo e mostrar logs periodicamente
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Verificar se jobs ainda estão a correr
        $backendStatus = (Get-Job -Id $backendJob.Id).State
        $frontendStatus = (Get-Job -Id $frontendJob.Id).State
        
        if ($backendStatus -ne "Running" -or $frontendStatus -ne "Running") {
            Write-Host ""
            Write-Host "⚠️  Um dos servidores parou!" -ForegroundColor Red
            Write-Host "Backend: $backendStatus" -ForegroundColor Yellow
            Write-Host "Frontend: $frontendStatus" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Logs do Backend:" -ForegroundColor Cyan
            Receive-Job -Id $backendJob.Id
            Write-Host ""
            Write-Host "Logs do Frontend:" -ForegroundColor Cyan
            Receive-Job -Id $frontendJob.Id
            break
        }
    }
} finally {
    # Cleanup quando o script termina
    Write-Host ""
    Write-Host "🛑 Parando servidores..." -ForegroundColor Yellow
    Stop-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
    Stop-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
    Write-Host "✅ Servidores parados" -ForegroundColor Green
    Write-Host ""
}

