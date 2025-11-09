# Build and Push Docker Images to ECR (Terraform)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Building and Pushing Docker Images" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get ECR URLs from Terraform output
Set-Location terraform

Write-Host "📊 Getting ECR repository URLs..." -ForegroundColor Yellow
$BACKEND_REPO = (terraform output -raw ecr_backend_repository_url)
$FRONTEND_REPO = (terraform output -raw ecr_frontend_repository_url)
$REGION = (terraform output -raw region)

Set-Location ..

if ([string]::IsNullOrEmpty($BACKEND_REPO) -or [string]::IsNullOrEmpty($FRONTEND_REPO)) {
    Write-Host "❌ Failed to get ECR URLs. Make sure Terraform has been applied." -ForegroundColor Red
    exit 1
}

Write-Host "Backend Repository:  $BACKEND_REPO" -ForegroundColor Cyan
Write-Host "Frontend Repository: $FRONTEND_REPO" -ForegroundColor Cyan
Write-Host ""

# Login to ECR
Write-Host "🔐 Logging in to ECR..." -ForegroundColor Yellow
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to login to ECR" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Logged in to ECR!" -ForegroundColor Green
Write-Host ""

# Build and push backend
Write-Host "🏗️  Building backend image..." -ForegroundColor Yellow
Set-Location backend

docker build -t lazysheeps-backend:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build backend image" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Backend image built!" -ForegroundColor Green

Write-Host "🚀 Pushing backend image..." -ForegroundColor Yellow
docker tag lazysheeps-backend:latest "${BACKEND_REPO}:latest"
docker push "${BACKEND_REPO}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push backend image" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Backend image pushed!" -ForegroundColor Green
Set-Location ..
Write-Host ""

# Build and push frontend
Write-Host "🏗️  Building frontend image..." -ForegroundColor Yellow
Set-Location frontend

docker build -t lazysheeps-frontend:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build frontend image" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Frontend image built!" -ForegroundColor Green

Write-Host "🚀 Pushing frontend image..." -ForegroundColor Yellow
docker tag lazysheeps-frontend:latest "${FRONTEND_REPO}:latest"
docker push "${FRONTEND_REPO}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push frontend image" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Frontend image pushed!" -ForegroundColor Green
Set-Location ..
Write-Host ""

Write-Host "============================================" -ForegroundColor Green
Write-Host "  ✅ All Images Pushed Successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Images:" -ForegroundColor Yellow
Write-Host "Backend:  $BACKEND_REPO:latest" -ForegroundColor Cyan
Write-Host "Frontend: $FRONTEND_REPO:latest" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Configure kubectl: aws eks update-kubeconfig --region $REGION --name lazysheeps-cluster" -ForegroundColor White
Write-Host "2. Check pods: kubectl get pods -n lazysheeps" -ForegroundColor White
Write-Host "3. Get frontend URL: kubectl get svc frontend-service -n lazysheeps" -ForegroundColor White
Write-Host ""
Write-Host "Note: Pods will automatically pull the new images!" -ForegroundColor Gray
Write-Host ""
