# ─────────────────────────────────────────────
#  CV Intellect — Start (Flask + ngrok)
# ─────────────────────────────────────────────

$PidFile = "$PSScriptRoot\.tunnel.pid"
$Port    = 5001

# ── Already running? ──────────────────────────
if (Test-Path $PidFile) {
    Write-Host "Tunnel already running. Run .\stop.ps1 first." -ForegroundColor Yellow
    exit
}

# ── Check ngrok authtoken ─────────────────────
$ngrokCfg = "$env:USERPROFILE\.config\ngrok\ngrok.yml"
$hasToken  = (Test-Path $ngrokCfg) -and (Select-String -Path $ngrokCfg -Pattern "authtoken" -Quiet)

if (-not $hasToken) {
    Write-Host ""
    Write-Host "  ngrok authtoken not found." -ForegroundColor Red
    Write-Host "  1. Sign up free at https://dashboard.ngrok.com/signup" -ForegroundColor Cyan
    Write-Host "  2. Copy your token from https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Cyan
    Write-Host "  3. Run:  ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Cyan
    Write-Host ""
    exit
}

Write-Host ""
Write-Host "  Starting CV Intellect..." -ForegroundColor Cyan

# ── Start Flask ───────────────────────────────
$flask = Start-Process python -ArgumentList "$PSScriptRoot\app.py" `
         -WorkingDirectory $PSScriptRoot `
         -PassThru -WindowStyle Minimized
Start-Sleep -Milliseconds 1500

# ── Start ngrok ───────────────────────────────
$ngrok = Start-Process ngrok -ArgumentList "http $Port" `
         -PassThru -WindowStyle Minimized
Start-Sleep -Seconds 2

# ── Fetch public URL from ngrok local API ─────
try {
    $info = Invoke-RestMethod "http://localhost:4040/api/tunnels" -ErrorAction Stop
    $url  = ($info.tunnels | Where-Object { $_.proto -eq "https" }).public_url
    if (-not $url) { $url = $info.tunnels[0].public_url }
} catch {
    $url = "(could not fetch — check http://localhost:4040)"
}

# ── Save PIDs for stop script ─────────────────
"$($flask.Id)`n$($ngrok.Id)" | Set-Content $PidFile

# ── Done ──────────────────────────────────────
Write-Host ""
Write-Host "  Flask  running  →  http://localhost:$Port" -ForegroundColor Green
Write-Host "  Public URL      →  $url"                   -ForegroundColor Green
Write-Host ""
Write-Host "  Run .\stop.ps1 to shut everything down." -ForegroundColor DarkGray
Write-Host ""
