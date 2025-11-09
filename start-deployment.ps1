# Quick Start Script for EKS Deployment
# This refreshes the PATH and starts deployment

Write-Host "Refreshing environment variables..." -ForegroundColor Cyan

# Refresh PATH to include newly installed AWS CLI
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify AWS CLI is available
Write-Host "Checking AWS CLI..." -ForegroundColor Yellow
aws --version

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] AWS CLI not found. Please restart PowerShell or run:" -ForegroundColor Red
    Write-Host '$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")' -ForegroundColor White
    exit 1
}

Write-Host "[OK] AWS CLI found!" -ForegroundColor Green
Write-Host ""

# Start the main deployment
& .\deploy-all.ps1
