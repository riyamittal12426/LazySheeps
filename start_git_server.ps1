# Quick Start Script for LazySheeps Git Server
# Run this to test your Git server

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  LazySheeps Git Server - Quick Start" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "📡 Checking backend server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -Method GET -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host "✅ Backend server is running on port 8000" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend server is NOT running" -ForegroundColor Red
    Write-Host "   Please start it with: python manage.py runserver" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if frontend is running
Write-Host "📡 Checking frontend server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5174" -Method GET -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host "✅ Frontend server is running on port 5174" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Frontend server is NOT running" -ForegroundColor Yellow
    Write-Host "   Start it with: cd frontend; npm run dev" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Open your browser:" -ForegroundColor White
Write-Host "   http://localhost:5174/my-repositories" -ForegroundColor Green
Write-Host ""

Write-Host "2. Click 'New Repository' to create your first repo" -ForegroundColor White
Write-Host ""

Write-Host "3. Copy the clone URL and use it locally:" -ForegroundColor White
Write-Host "   cd your-project" -ForegroundColor Gray
Write-Host "   git init" -ForegroundColor Gray
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m 'Initial commit'" -ForegroundColor Gray
Write-Host "   git remote add origin <clone-url>" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Browse your code in the web UI!" -ForegroundColor White
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Run Automated Tests (Optional)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "To run the test suite:" -ForegroundColor White
Write-Host '  $env:LAZYSHEEPS_TOKEN = "your_jwt_token"' -ForegroundColor Gray
Write-Host "  python backend\test_git_server.py" -ForegroundColor Gray
Write-Host ""

Write-Host "Get your token from localStorage in browser devtools" -ForegroundColor Yellow
Write-Host "(F12 → Application → Local Storage → access_token)" -ForegroundColor Yellow
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Documentation" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📖 User Guide: GIT_SERVER_GUIDE.md" -ForegroundColor White
Write-Host "📝 Implementation: GIT_SERVER_COMPLETE.md" -ForegroundColor White
Write-Host ""

Write-Host "Happy coding! 🚀" -ForegroundColor Green
