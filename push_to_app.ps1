# Quick Push to LazySheeps Script
# This script helps you push your code to your LazySheeps app

param(
    [string]$RepoName = "lazysheeps",
    [string]$Message = "Update code"
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Push Code to LazySheeps App" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "📡 Checking backend server..." -ForegroundColor Yellow
try {
    $null = Invoke-WebRequest -Uri "http://localhost:8000" -Method GET -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Backend server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend server is NOT running!" -ForegroundColor Red
    Write-Host "   Please start it first:" -ForegroundColor Yellow
    Write-Host "   cd backend; python manage.py runserver" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "📝 Repository: $RepoName" -ForegroundColor White
Write-Host "💬 Commit Message: $Message" -ForegroundColor White
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "❌ Not in a Git repository!" -ForegroundColor Red
    Write-Host "   Run 'git init' first or navigate to your project folder" -ForegroundColor Yellow
    exit 1
}

# Check if remote exists
$remotes = git remote
if ($remotes -notcontains "lazysheeps") {
    Write-Host "⚠️  Remote 'lazysheeps' not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Let me help you set it up:" -ForegroundColor White
    Write-Host ""
    
    # Get username
    $username = Read-Host "Enter your LazySheeps username"
    
    Write-Host ""
    Write-Host "🔧 Adding remote..." -ForegroundColor Yellow
    
    $remoteUrl = "http://localhost:8000/git/$username/$RepoName.git"
    git remote add lazysheeps $remoteUrl
    
    Write-Host "✅ Remote added: $remoteUrl" -ForegroundColor Green
    Write-Host ""
}

# Show current status
Write-Host "📊 Git Status:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Ask for confirmation
$confirm = Read-Host "Do you want to commit and push? (Y/n)"
if ($confirm -eq "" -or $confirm -eq "Y" -or $confirm -eq "y") {
    
    Write-Host ""
    Write-Host "📦 Staging all changes..." -ForegroundColor Yellow
    git add .
    
    Write-Host "💾 Committing..." -ForegroundColor Yellow
    git commit -m $Message
    
    Write-Host "⬆️  Pushing to LazySheeps..." -ForegroundColor Yellow
    
    # Try to push
    try {
        git push lazysheeps main 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Successfully pushed to LazySheeps!" -ForegroundColor Green
            Write-Host ""
            Write-Host "🌐 View your code at:" -ForegroundColor White
            Write-Host "   http://localhost:5174/my-repositories" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "⚠️  Push had issues. Trying with force..." -ForegroundColor Yellow
            git push -f lazysheeps main 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Force push successful!" -ForegroundColor Green
            } else {
                Write-Host "❌ Push failed!" -ForegroundColor Red
                Write-Host ""
                Write-Host "Possible issues:" -ForegroundColor Yellow
                Write-Host "1. Repository '$RepoName' doesn't exist on LazySheeps" -ForegroundColor Gray
                Write-Host "   → Create it via: http://localhost:5174/my-repositories" -ForegroundColor Gray
                Write-Host "2. You're not logged in" -ForegroundColor Gray
                Write-Host "   → Login at: http://localhost:5174" -ForegroundColor Gray
                Write-Host "3. Wrong username in remote URL" -ForegroundColor Gray
                Write-Host "   → Check with: git remote -v" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
    
} else {
    Write-Host "❌ Push cancelled" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Show instructions
Write-Host "💡 Useful commands:" -ForegroundColor White
Write-Host "   .\push_to_app.ps1 -RepoName 'my-project' -Message 'Fix bug'" -ForegroundColor Gray
Write-Host "   git remote -v  # View all remotes" -ForegroundColor Gray
Write-Host "   git push lazysheeps main  # Manual push" -ForegroundColor Gray
Write-Host ""
