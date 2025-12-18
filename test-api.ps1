# Quick API Test Script
Write-Host "Testing Backend API..." -ForegroundColor Cyan

$body = @{
    productName = "TestProduct"
    description = "A test product description"
    mood = 50
    energy = 50
    style = "cinematic"
    archetype = "hero-journey"
} | ConvertTo-Json

try {
    Write-Host "`nSending request to http://localhost:8001/api/generate-script..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/generate-script" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    
    Write-Host "`n✅ SUCCESS!" -ForegroundColor Green
    Write-Host "Response success: $($response.success)" -ForegroundColor Green
    Write-Host "Script length: $($response.script.Length) characters" -ForegroundColor Green
    Write-Host "Number of scenes: $($response.scenes.Count)" -ForegroundColor Green
    Write-Host "`nFirst 200 chars of script:" -ForegroundColor Cyan
    Write-Host $response.script.Substring(0, [Math]::Min(200, $response.script.Length))
} catch {
    Write-Host "`n❌ ERROR!" -ForegroundColor Red
    Write-Host "Error message: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nMake sure the backend is running:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  python -m uvicorn main:app --reload --port 8001" -ForegroundColor White
}

