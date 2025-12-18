# Backend Server Startup Script
Write-Host "=== Starting Backend Server ===" -ForegroundColor Cyan

$backendPath = "C:\Users\surya\OneDrive\Desktop\work\projects\personal_proj\Advertising\backend"

# Kill any existing processes on port 8002
Write-Host "Cleaning up existing processes on port 8002..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# Start the backend
Write-Host "Starting backend on http://127.0.0.1:8002..." -ForegroundColor Green
Set-Location $backendPath
Start-Process python -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8002", "--reload" -WindowStyle Normal

Write-Host "`nBackend server starting in new window..." -ForegroundColor Green
Write-Host "Wait 5-10 seconds, then test with:" -ForegroundColor Yellow
Write-Host "  http://localhost:8002/api/health" -ForegroundColor White
Write-Host "`nOr use the frontend at http://localhost:3000" -ForegroundColor Cyan

