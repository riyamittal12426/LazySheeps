# Master Deployment Script for LazySheeps on AWS EKS
# This script orchestrates the entire deployment process

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host " LazySheeps - AWS EKS Full Deployment" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "1. Create EKS cluster (15-20 minutes)" -ForegroundColor White
Write-Host "2. Install AWS Load Balancer Controller" -ForegroundColor White
Write-Host "3. Install EBS CSI Driver" -ForegroundColor White
Write-Host "4. Build and push Docker images to ECR" -ForegroundColor White
Write-Host "5. Update Kubernetes manifests" -ForegroundColor White
Write-Host "6. Deploy all services to EKS" -ForegroundColor White
Write-Host ""
Write-Host "COST ESTIMATE: Approximately $1-2 for 2 hours" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Do you want to continue? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "Deployment cancelled." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "Starting deployment..." -ForegroundColor Green
Write-Host ""

# Record start time
$startTime = Get-Date

try {
    # Step 1: Create EKS Cluster
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "STEP 1/4: Creating EKS Cluster" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    
    & .\deploy-eks.ps1
    
    if ($LASTEXITCODE -ne 0) {
        throw "EKS cluster creation failed"
    }
    
    Write-Host ""
    Write-Host "[SUCCESS] Step 1 Complete: EKS Cluster Ready" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 3
    
    # Step 2: Build and Push Docker Images
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "STEP 2/4: Building and Pushing Docker Images" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    
    & .\deploy-images.ps1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker images build/push failed"
    }
    
    Write-Host ""
    Write-Host "[SUCCESS] Step 2 Complete: Images in ECR" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 3
    
    # Step 3: Update Kubernetes Manifests
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "STEP 3/4: Updating Kubernetes Manifests" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    
    & .\update-k8s-manifests.ps1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Manifest update failed"
    }
    
    Write-Host ""
    Write-Host "[SUCCESS] Step 3 Complete: Manifests Updated" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 3
    
    # Step 4: Deploy to Kubernetes
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "STEP 4/4: Deploying to Kubernetes" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    
    & .\deploy-k8s.ps1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Kubernetes deployment failed"
    }
    
    Write-Host ""
    Write-Host "[SUCCESS] Step 4 Complete: Application Deployed" -ForegroundColor Green
    Write-Host ""
    
    # Calculate total time
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "    DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Total deployment time: $($duration.Minutes) minutes $($duration.Seconds) seconds" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Wait 2-3 minutes for Ingress to provision the Load Balancer" -ForegroundColor White
    Write-Host "2. Get your URL: kubectl get ingress lazysheeps-ingress -n lazysheeps" -ForegroundColor White
    Write-Host "3. Access your application in the browser" -ForegroundColor White
    Write-Host ""
    Write-Host "Remember to delete resources after testing to avoid charges!" -ForegroundColor Yellow
    Write-Host "Cleanup: .\cleanup-eks.ps1" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "    DEPLOYMENT FAILED!" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the logs above for details." -ForegroundColor Yellow
    Write-Host "You can retry individual steps or run cleanup script" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
