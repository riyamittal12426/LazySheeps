# LazySheeps EKS Deployment Script
# This script will deploy your application to AWS EKS

Write-Host "🚀 LazySheeps AWS EKS Deployment" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$CLUSTER_NAME = "lazysheeps-cluster"
$REGION = "us-east-1"
$NODE_TYPE = "t3.medium"
$MIN_NODES = 2
$MAX_NODES = 4
$DESIRED_NODES = 2

# Step 1: Create EKS Cluster
Write-Host "📦 Step 1: Creating EKS Cluster..." -ForegroundColor Yellow
Write-Host "This will take 15-20 minutes. Please be patient..." -ForegroundColor Gray
Write-Host ""

$eksctlPath = "$env:USERPROFILE\eksctl\eksctl.exe"

& $eksctlPath create cluster `
    --name $CLUSTER_NAME `
    --region $REGION `
    --nodegroup-name lazysheeps-nodes `
    --node-type $NODE_TYPE `
    --nodes $DESIRED_NODES `
    --nodes-min $MIN_NODES `
    --nodes-max $MAX_NODES `
    --managed

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create EKS cluster" -ForegroundColor Red
    exit 1
}

Write-Host "✅ EKS Cluster created successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Update kubeconfig
Write-Host "📝 Step 2: Updating kubeconfig..." -ForegroundColor Yellow
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to update kubeconfig" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Kubeconfig updated!" -ForegroundColor Green
Write-Host ""

# Step 3: Verify connection
Write-Host "🔍 Step 3: Verifying cluster connection..." -ForegroundColor Yellow
kubectl get nodes

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to connect to cluster" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Connected to cluster!" -ForegroundColor Green
Write-Host ""

# Step 4: Install AWS Load Balancer Controller
Write-Host "🔧 Step 4: Installing AWS Load Balancer Controller..." -ForegroundColor Yellow
Write-Host "This is required for the Ingress to work..." -ForegroundColor Gray

# Download IAM policy
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.6.0/docs/install/iam_policy.json" -OutFile "iam_policy.json"

# Get AWS account ID
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
Write-Host "AWS Account ID: $ACCOUNT_ID" -ForegroundColor Gray

# Create IAM policy
aws iam create-policy `
    --policy-name AWSLoadBalancerControllerIAMPolicy `
    --policy-document file://iam_policy.json

# Create service account (ignore if already exists)
& $eksctlPath create iamserviceaccount `
    --cluster=$CLUSTER_NAME `
    --namespace=kube-system `
    --name=aws-load-balancer-controller `
    --attach-policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy `
    --override-existing-serviceaccounts `
    --approve

# Install AWS Load Balancer Controller using kubectl
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"

Write-Host "✅ AWS Load Balancer Controller prerequisites installed!" -ForegroundColor Green
Write-Host ""

# Step 5: Install EBS CSI Driver
Write-Host "💾 Step 5: Installing EBS CSI Driver..." -ForegroundColor Yellow
Write-Host "This is required for PostgreSQL persistent storage..." -ForegroundColor Gray

& $eksctlPath create iamserviceaccount `
    --name ebs-csi-controller-sa `
    --namespace kube-system `
    --cluster $CLUSTER_NAME `
    --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy `
    --approve `
    --role-only `
    --role-name AmazonEKS_EBS_CSI_DriverRole

aws eks create-addon `
    --cluster-name $CLUSTER_NAME `
    --addon-name aws-ebs-csi-driver `
    --service-account-role-arn arn:aws:iam::${ACCOUNT_ID}:role/AmazonEKS_EBS_CSI_DriverRole

Write-Host "✅ EBS CSI Driver installed!" -ForegroundColor Green
Write-Host ""

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ EKS Cluster Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Build and push Docker images to ECR (see deploy-images.ps1)" -ForegroundColor White
Write-Host "2. Update k8s manifests with your ECR URLs" -ForegroundColor White
Write-Host "3. Deploy application: kubectl apply -f k8s/" -ForegroundColor White
Write-Host ""
Write-Host "Cluster Name: $CLUSTER_NAME" -ForegroundColor Cyan
Write-Host "Region: $REGION" -ForegroundColor Cyan
Write-Host ""
