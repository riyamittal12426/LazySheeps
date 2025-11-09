# LazySheeps Docker Images Build and Push to ECR
# This script builds and pushes your Docker images to AWS ECR

Write-Host "🐳 LazySheeps Docker Images - ECR Push" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$REGION = "us-east-1"
$BACKEND_REPO = "lazysheeps-backend"
$FRONTEND_REPO = "lazysheeps-frontend"

# Get AWS account ID
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
Write-Host "AWS Account ID: $ACCOUNT_ID" -ForegroundColor Cyan
Write-Host "Region: $REGION" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create ECR repositories
Write-Host "📦 Step 1: Creating ECR repositories..." -ForegroundColor Yellow

Write-Host "Creating backend repository..." -ForegroundColor Gray
aws ecr create-repository --repository-name $BACKEND_REPO --region $REGION 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend repository created!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Backend repository already exists" -ForegroundColor Gray
}

Write-Host "Creating frontend repository..." -ForegroundColor Gray
aws ecr create-repository --repository-name $FRONTEND_REPO --region $REGION 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend repository created!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Frontend repository already exists" -ForegroundColor Gray
}

Write-Host ""

# Step 2: Login to ECR
Write-Host "🔐 Step 2: Logging in to ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to login to ECR" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Logged in to ECR!" -ForegroundColor Green
Write-Host ""

# Step 3: Build and push backend
Write-Host "🏗️  Step 3: Building backend image..." -ForegroundColor Yellow
Set-Location backend

docker build -t ${BACKEND_REPO}:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build backend image" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Backend image built!" -ForegroundColor Green

Write-Host "🚀 Tagging and pushing backend image..." -ForegroundColor Yellow
docker tag ${BACKEND_REPO}:latest "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${BACKEND_REPO}:latest"
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${BACKEND_REPO}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push backend image" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Backend image pushed to ECR!" -ForegroundColor Green
Set-Location ..
Write-Host ""

# Step 4: Build and push frontend
Write-Host "🏗️  Step 4: Building frontend image..." -ForegroundColor Yellow
Set-Location frontend

docker build -t ${FRONTEND_REPO}:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build frontend image" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Frontend image built!" -ForegroundColor Green

Write-Host "🚀 Tagging and pushing frontend image..." -ForegroundColor Yellow
docker tag ${FRONTEND_REPO}:latest "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${FRONTEND_REPO}:latest"
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${FRONTEND_REPO}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push frontend image" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Frontend image pushed to ECR!" -ForegroundColor Green
Set-Location ..
Write-Host ""

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ All Images Pushed to ECR!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend Image:" -ForegroundColor Yellow
Write-Host "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${BACKEND_REPO}:latest" -ForegroundColor White
Write-Host ""
Write-Host "Frontend Image:" -ForegroundColor Yellow
Write-Host "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${FRONTEND_REPO}:latest" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "Run: .\update-k8s-manifests.ps1" -ForegroundColor White
Write-Host "This will automatically update your Kubernetes manifests with these image URLs" -ForegroundColor Gray
Write-Host ""
