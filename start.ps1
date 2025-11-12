# ShortlistAI - Script de início único (uma consola)
# Lança Backend (FastAPI) e Frontend (Vite) na mesma janela

$ErrorActionPreference = "Stop"

# Ensure we run from repository root
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host ""
Write-Host "========================================"
Write-Host "  Starting ShortlistAI (single console)"
Write-Host "========================================"
Write-Host ""

$backendDir = Join-Path (Get-Location) "src\backend"
$frontendDir = Join-Path (Get-Location) "src\frontend"
$backendExe = Join-Path $backendDir "venv\Scripts\python.exe"
$backendMain = Join-Path $backendDir "main.py"

if (-not (Test-Path $backendExe)) {
    throw "Backend virtualenv not found at $backendExe. Create it with 'python -m venv src\backend\venv'."
}
if (-not (Test-Path $backendMain)) {
    throw "Cannot find main.py in $backendDir."
}

$npmCommand = (Get-Command "npm.cmd" -ErrorAction Stop).Source

function Stop-Processes {
    param([string[]] $Names)
    foreach ($name in $Names) {
        Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host ("Stopping leftover process {0} (PID {1})..." -f $_.ProcessName, $_.Id)
            try {
                $_.Kill()
                $_.WaitForExit()
            } catch {
                # ignore errors
            }
        }
    }
}

Stop-Processes @("python", "node")
Write-Host "Old python/node processes stopped."
Write-Host ""

function Start-ConsoleProcess {
    param(
        [string] $FilePath,
        [string] $Arguments,
        [string] $WorkingDirectory,
        [string] $Label
    )

    Write-Host ("Starting {0}..." -f $Label)

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = $Arguments
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $true  # Changed to TRUE to show console windows
    $psi.CreateNoWindow = $false

    $process = [System.Diagnostics.Process]::Start($psi)
    if (-not $process) {
        throw "Failed to start $Label."
    }

    Write-Host ("  PID: {0}" -f $process.Id)
    return $process
}

$backendProcess = Start-ConsoleProcess $backendExe "main.py" $backendDir "Backend (FastAPI)"
Start-Sleep -Seconds 2
$frontendProcess = Start-ConsoleProcess $npmCommand "run dev" $frontendDir "Frontend (Vite dev server)"

Write-Host ""
Write-Host "========================================"
Write-Host " ShortlistAI running"
Write-Host " Backend : http://localhost:8000"
Write-Host " Frontend: http://localhost:3000"
Write-Host "========================================"
Write-Host "Press Ctrl+C to stop both servers."
Write-Host ""

try {
    while ($true) {
        if ($backendProcess.HasExited) {
            throw "Backend process exited with code $($backendProcess.ExitCode)."
        }
        if ($frontendProcess.HasExited) {
            throw "Frontend process exited with code $($frontendProcess.ExitCode)."
        }
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host ""
    Write-Host $_ -ForegroundColor Yellow
} finally {
    foreach ($proc in @($frontendProcess, $backendProcess)) {
        if ($proc -and -not $proc.HasExited) {
            Write-Host ("Stopping {0} (PID {1})..." -f $proc.ProcessName, $proc.Id)
            try {
                $proc.Kill()
                $proc.WaitForExit(5000) | Out-Null
            } catch {
                # ignore
            }
        }
    }

    Stop-Processes @("python", "node")
    Write-Host ""
    Write-Host "Servers stopped."
}

