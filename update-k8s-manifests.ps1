# Update Kubernetes manifests with ECR image URLs
# This script automatically updates the deployment files with your ECR registry URLs

Write-Host "📝 Updating Kubernetes Manifests" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$REGION = "us-east-1"
$BACKEND_REPO = "lazysheeps-backend"
$FRONTEND_REPO = "lazysheeps-frontend"

# Get AWS account ID
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)

if ([string]::IsNullOrEmpty($ACCOUNT_ID)) {
    Write-Host "❌ Failed to get AWS Account ID. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

Write-Host "AWS Account ID: $ACCOUNT_ID" -ForegroundColor Cyan
Write-Host "Region: $REGION" -ForegroundColor Cyan
Write-Host ""

# Image URLs
$BACKEND_IMAGE = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${BACKEND_REPO}:latest"
$FRONTEND_IMAGE = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${FRONTEND_REPO}:latest"

# Update backend-deployment.yaml
Write-Host "📄 Updating backend-deployment.yaml..." -ForegroundColor Yellow
$backendDeployment = Get-Content "k8s\backend-deployment.yaml" -Raw
$backendDeployment = $backendDeployment -replace 'image: your-registry/lazysheeps-backend:latest.*', "image: $BACKEND_IMAGE"
$backendDeployment | Set-Content "k8s\backend-deployment.yaml"
Write-Host "✅ Backend deployment updated!" -ForegroundColor Green

# Update frontend-deployment.yaml
Write-Host "📄 Updating frontend-deployment.yaml..." -ForegroundColor Yellow
$frontendDeployment = Get-Content "k8s\frontend-deployment.yaml" -Raw
$frontendDeployment = $frontendDeployment -replace 'image: your-registry/lazysheeps-frontend:latest.*', "image: $FRONTEND_IMAGE"
$frontendDeployment | Set-Content "k8s\frontend-deployment.yaml"
Write-Host "✅ Frontend deployment updated!" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Manifests Updated Successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Updated Images:" -ForegroundColor Yellow
Write-Host "Backend:  $BACKEND_IMAGE" -ForegroundColor White
Write-Host "Frontend: $FRONTEND_IMAGE" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update secrets in k8s/secret.yaml (base64 encode your passwords)" -ForegroundColor White
Write-Host "2. Deploy: .\deploy-k8s.ps1" -ForegroundColor White
Write-Host ""
