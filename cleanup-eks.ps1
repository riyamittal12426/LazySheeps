# Cleanup Script - Delete all AWS EKS resources
# This script removes all resources to avoid ongoing charges

Write-Host ""
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║        LazySheeps EKS Cleanup Script      ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  WARNING: This will delete:" -ForegroundColor Red
Write-Host "- EKS Cluster (lazysheeps-cluster)" -ForegroundColor White
Write-Host "- All deployed applications and data" -ForegroundColor White
Write-Host "- ECR repositories (Docker images)" -ForegroundColor White
Write-Host "- Load Balancers and EBS volumes" -ForegroundColor White
Write-Host ""

$confirmation = Read-Host "Are you sure you want to delete everything? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "Cleanup cancelled." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Yellow
Write-Host ""

$CLUSTER_NAME = "lazysheeps-cluster"
$REGION = "us-east-1"
$eksctlPath = "$env:USERPROFILE\eksctl\eksctl.exe"

# Step 1: Delete Kubernetes resources
Write-Host "🗑️  Step 1: Deleting Kubernetes resources..." -ForegroundColor Yellow
kubectl delete -f k8s/ --ignore-not-found=true

Write-Host "✅ Kubernetes resources deleted!" -ForegroundColor Green
Write-Host ""

# Step 2: Delete namespace
Write-Host "🗑️  Step 2: Deleting namespace..." -ForegroundColor Yellow
kubectl delete namespace lazysheeps --ignore-not-found=true

Write-Host "✅ Namespace deleted!" -ForegroundColor Green
Write-Host ""

# Wait for resources to be fully deleted
Write-Host "⏳ Waiting for resources to be fully deleted..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# Step 3: Delete EKS Cluster
Write-Host "🗑️  Step 3: Deleting EKS cluster..." -ForegroundColor Yellow
Write-Host "This may take 10-15 minutes..." -ForegroundColor Gray

& $eksctlPath delete cluster --name $CLUSTER_NAME --region $REGION --wait

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ EKS cluster deleted!" -ForegroundColor Green
} else {
    Write-Host "⚠️  EKS cluster deletion may have failed. Check AWS console." -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Delete ECR repositories
Write-Host "🗑️  Step 4: Deleting ECR repositories..." -ForegroundColor Yellow

aws ecr delete-repository --repository-name lazysheeps-backend --region $REGION --force 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend repository deleted!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Backend repository may not exist" -ForegroundColor Gray
}

aws ecr delete-repository --repository-name lazysheeps-frontend --region $REGION --force 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend repository deleted!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Frontend repository may not exist" -ForegroundColor Gray
}

Write-Host ""

# Step 5: Delete IAM policies and roles
Write-Host "🗑️  Step 5: Cleaning up IAM policies..." -ForegroundColor Yellow

$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)

# Detach and delete LoadBalancer policy
$policyArn = "arn:aws:iam::${ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy"
aws iam delete-policy --policy-arn $policyArn 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ IAM policies deleted!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Some IAM resources may need manual cleanup" -ForegroundColor Gray
}

Write-Host ""

# Cleanup local files
Write-Host "🗑️  Step 6: Cleaning up local files..." -ForegroundColor Yellow
Remove-Item "iam_policy.json" -ErrorAction SilentlyContinue
Write-Host "✅ Local files cleaned!" -ForegroundColor Green
Write-Host ""

Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          ✅ CLEANUP COMPLETE! ✅           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "All AWS resources have been deleted." -ForegroundColor Cyan
Write-Host "You will no longer be charged for EKS services." -ForegroundColor Cyan
Write-Host ""
Write-Host "Verification:" -ForegroundColor Yellow
Write-Host "Check AWS Console to ensure all resources are deleted:" -ForegroundColor White
Write-Host "- EC2 Dashboard (Load Balancers, Volumes)" -ForegroundColor Gray
Write-Host "- EKS Dashboard (Clusters)" -ForegroundColor Gray
Write-Host "- ECR Dashboard (Repositories)" -ForegroundColor Gray
Write-Host ""
