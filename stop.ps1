# ─────────────────────────────────────────────
#  CV Intellect — Stop (Flask + ngrok)
# ─────────────────────────────────────────────

$PidFile = "$PSScriptRoot\.tunnel.pid"

if (-not (Test-Path $PidFile)) {
    Write-Host "Nothing is running (no .tunnel.pid found)." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "  Stopping CV Intellect..." -ForegroundColor Cyan

$pids = Get-Content $PidFile

foreach ($id in $pids) {
    $id = $id.Trim()
    if ($id -match '^\d+$') {
        try {
            Stop-Process -Id $id -Force -ErrorAction Stop
            Write-Host "  Stopped PID $id" -ForegroundColor Green
        } catch {
            Write-Host "  PID $id already gone" -ForegroundColor DarkGray
        }
    }
}

# Also kill any stray ngrok / python processes on port 5001
Get-Process -Name "ngrok"  -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -eq "" } |
    ForEach-Object {
        $conn = netstat -ano | Select-String ":5001"
        if ($conn -match $_.Id) { Stop-Process -Id $_.Id -Force }
    }

Remove-Item $PidFile -Force
Write-Host "  All stopped." -ForegroundColor Green
Write-Host ""
