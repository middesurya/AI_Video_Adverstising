# Start Backend Server Script
Write-Host "Starting Backend Server..." -ForegroundColor Cyan

$backendPath = "C:\Users\surya\OneDrive\Desktop\work\projects\personal_proj\Advertising\backend"

# Kill any existing Python processes on port 8001
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# Start the backend
Write-Host "Starting backend on http://127.0.0.1:8001..." -ForegroundColor Green
Set-Location $backendPath
Start-Process python -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001", "--reload" -WindowStyle Normal

Write-Host "`nBackend should be starting..." -ForegroundColor Green
Write-Host "Wait 3-5 seconds, then test with:" -ForegroundColor Yellow
Write-Host "  http://localhost:8001/health" -ForegroundColor White
Write-Host "`nOr refresh your browser page!" -ForegroundColor Cyan

