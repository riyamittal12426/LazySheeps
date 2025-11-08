# Quick Login Test for LazySheeps

Write-Host "Testing Authentication..." -ForegroundColor Cyan
Write-Host ""

# Test if backend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -Method GET -UseBasicParsing -TimeoutSec 2
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not running!" -ForegroundColor Red
    Write-Host "   Start it with: cd backend; python manage.py runserver" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  To use the Git server, you need to:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Login to get your authentication token:" -ForegroundColor White
Write-Host "   → Open: http://localhost:5174" -ForegroundColor Cyan
Write-Host "   → Login or Register" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Get your token from browser:" -ForegroundColor White
Write-Host "   → Press F12 (DevTools)" -ForegroundColor Gray
Write-Host "   → Go to 'Application' tab" -ForegroundColor Gray
Write-Host "   → Click 'Local Storage' → 'http://localhost:5174'" -ForegroundColor Gray
Write-Host "   → Copy the 'access_token' value" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Test with curl (Windows):" -ForegroundColor White
Write-Host '   $token = "YOUR_TOKEN_HERE"' -ForegroundColor Gray
Write-Host '   curl -X POST http://localhost:8000/api/git/create/ `' -ForegroundColor Gray
Write-Host '        -H "Authorization: Bearer $token" `' -ForegroundColor Gray
Write-Host '        -H "Content-Type: application/json" `' -ForegroundColor Gray
Write-Host '        -d ''{"name": "test-repo", "description": "Test repository"}''' -ForegroundColor Gray
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  The error you saw:" -ForegroundColor Yellow
Write-Host '  "Unauthorized: /api/git/create/"' -ForegroundColor Red
Write-Host ""
Write-Host "  Means: You need to login first!" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Quick fix:" -ForegroundColor Green
Write-Host "1. Open http://localhost:5174 in your browser" -ForegroundColor White
Write-Host "2. Click 'Login' or 'Register'" -ForegroundColor White  
Write-Host "3. After login, try creating a repository again!" -ForegroundColor White
Write-Host ""
