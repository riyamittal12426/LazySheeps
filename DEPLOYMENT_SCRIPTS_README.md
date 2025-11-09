# 🚀 LazySheeps AWS EKS Deployment Scripts

Complete automation scripts for deploying LazySheeps to AWS EKS (Elastic Kubernetes Service).

## 📋 Prerequisites

### Required
- ✅ AWS Account with appropriate permissions
- ✅ AWS CLI (installed automatically)
- ✅ kubectl (already installed)
- ✅ Docker Desktop (already installed)
- ✅ eksctl (installed automatically)
- ✅ AWS credentials configured

### AWS Permissions Needed
Your AWS user/role needs permissions for:
- EKS (create clusters, nodegroups)
- EC2 (instances, security groups, load balancers)
- IAM (create policies, roles, service accounts)
- ECR (create repositories, push images)
- EBS (create volumes)

## 💰 Cost Estimate

### For 1-2 hours of testing:
- **Total: ~$1-2 USD**
  - EKS Control Plane: $0.20
  - EC2 Nodes (2x t3.medium): $0.16
  - Load Balancer: $0.05
  - EBS Storage: <$0.01

### For 24 hours:
- **Total: ~$12 USD**

### Monthly (if kept running):
- **Total: ~$150-300 USD**
  - EKS Control Plane: $72/month
  - EC2 Nodes: $60-120/month
  - Load Balancer: $16/month
  - Storage: ~$2/month

## 🎯 Quick Start (One Command)

### Option 1: Full Automated Deployment

```powershell
# Deploy everything with one command
.\deploy-all.ps1
```

This will:
1. Create EKS cluster (~15-20 minutes)
2. Install AWS Load Balancer Controller
3. Install EBS CSI Driver
4. Build and push Docker images to ECR
5. Update Kubernetes manifests
6. Deploy all services

**Total time: ~25-30 minutes**

### Option 2: Step-by-Step Deployment

If you prefer to run each step manually:

```powershell
# Step 1: Create EKS cluster
.\deploy-eks.ps1

# Step 2: Build and push images
.\deploy-images.ps1

# Step 3: Update manifests
.\update-k8s-manifests.ps1

# Step 4: Deploy to Kubernetes
.\deploy-k8s.ps1
```

## 📝 Individual Scripts

### 1. `deploy-all.ps1`
**Master script that runs everything**
- Orchestrates the entire deployment
- Error handling and progress tracking
- Recommended for first-time deployment

```powershell
.\deploy-all.ps1
```

### 2. `deploy-eks.ps1`
**Creates EKS cluster and prerequisites**
- Creates EKS cluster with managed node group
- Installs AWS Load Balancer Controller
- Installs EBS CSI Driver
- Configures kubeconfig

```powershell
.\deploy-eks.ps1
```

### 3. `deploy-images.ps1`
**Builds and pushes Docker images to ECR**
- Creates ECR repositories
- Builds backend and frontend images
- Pushes images to ECR
- Displays image URLs

```powershell
.\deploy-images.ps1
```

### 4. `update-k8s-manifests.ps1`
**Updates Kubernetes manifests with your ECR URLs**
- Automatically gets your AWS account ID
- Updates backend-deployment.yaml
- Updates frontend-deployment.yaml

```powershell
.\update-k8s-manifests.ps1
```

### 5. `deploy-k8s.ps1`
**Deploys all Kubernetes resources**
- Creates namespace, ConfigMap, Secrets
- Deploys PostgreSQL with persistent storage
- Deploys Backend and Frontend
- Creates Ingress and HPA
- Runs database migrations

```powershell
.\deploy-k8s.ps1
```

### 6. `cleanup-eks.ps1`
**Deletes all AWS resources**
- Deletes Kubernetes resources
- Deletes EKS cluster
- Deletes ECR repositories
- Cleans up IAM policies

```powershell
.\cleanup-eks.ps1
```

## 🔧 Configuration

### AWS Region
Default: `us-east-1`

To change, edit these variables in the scripts:
```powershell
$REGION = "us-west-2"  # Change to your preferred region
```

### Cluster Configuration
Default settings in `deploy-eks.ps1`:
```powershell
$CLUSTER_NAME = "lazysheeps-cluster"
$NODE_TYPE = "t3.medium"
$MIN_NODES = 2
$MAX_NODES = 4
$DESIRED_NODES = 2
```

### Kubernetes Secrets
Before deploying, update `k8s/secret.yaml` with your secrets:

```powershell
# Generate base64 encoded values in PowerShell
$text = "your-password"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
[Convert]::ToBase64String($bytes)
```

Required secrets:
- `POSTGRES_PASSWORD` - Database password
- `SECRET_KEY` - Django secret key
- `GITHUB_CLIENT_ID` - (Optional) GitHub OAuth
- `GITHUB_CLIENT_SECRET` - (Optional) GitHub OAuth

## 📊 Monitoring

### Check Deployment Status

```powershell
# View all resources
kubectl get all -n lazysheeps

# View pods
kubectl get pods -n lazysheeps

# View services
kubectl get svc -n lazysheeps

# View ingress (get URL)
kubectl get ingress -n lazysheeps
```

### View Logs

```powershell
# Backend logs
kubectl logs -f deployment/backend -n lazysheeps

# Frontend logs
kubectl logs -f deployment/frontend -n lazysheeps

# PostgreSQL logs
kubectl logs -f statefulset/postgres -n lazysheeps
```

### Access Application

```powershell
# Get the Ingress URL
kubectl get ingress lazysheeps-ingress -n lazysheeps -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

Wait 2-3 minutes after deployment for the Load Balancer to be provisioned, then access your app at the URL shown.

## 🔍 Troubleshooting

### Pods Not Starting

```powershell
# Describe pod to see events
kubectl describe pod <pod-name> -n lazysheeps

# Check logs
kubectl logs <pod-name> -n lazysheeps
```

### Ingress Not Working

```powershell
# Check ingress events
kubectl describe ingress lazysheeps-ingress -n lazysheeps

# Check ALB controller logs
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

### Database Connection Issues

```powershell
# Test database connection
kubectl exec -it <backend-pod-name> -n lazysheeps -- python manage.py dbshell
```

### EKS Cluster Creation Failed

```powershell
# Check CloudFormation stacks
aws cloudformation describe-stacks --region us-east-1

# View eksctl logs
# Check the terminal output for errors
```

## 🧹 Cleanup

### After Testing (Important!)

To avoid ongoing charges, delete all resources:

```powershell
.\cleanup-eks.ps1
```

This will:
- Delete all Kubernetes resources
- Delete EKS cluster
- Delete ECR repositories
- Clean up IAM policies
- Remove local files

**Verify in AWS Console:**
- EC2 Dashboard → Load Balancers (should be empty)
- EKS Dashboard → Clusters (should be empty)
- ECR Dashboard → Repositories (should be empty)
- EC2 Dashboard → Volumes (should be empty)

## 📚 Additional Resources

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)

## 🆘 Support

If you encounter issues:

1. Check the logs: `kubectl logs -f deployment/backend -n lazysheeps`
2. Describe resources: `kubectl describe pod <pod-name> -n lazysheeps`
3. Check AWS CloudWatch logs
4. Review EKS cluster events in AWS Console

## ⚠️ Important Notes

- **Remember to run cleanup** after testing to avoid charges
- Load Balancer takes 2-3 minutes to provision
- First deployment takes ~25-30 minutes
- Subsequent deployments (updates) take ~5 minutes
- Database data is persistent (stored in EBS volume)
- Delete the cluster when not in use to save costs

## 📝 What Gets Deployed

### Infrastructure
- EKS Control Plane (managed by AWS)
- 2x t3.medium EC2 instances (worker nodes)
- Application Load Balancer (ALB)
- EBS Volume (10GB for PostgreSQL)
- VPC with public/private subnets

### Applications
- PostgreSQL 15 (with persistent storage)
- Django Backend (3 replicas, auto-scaling 2-10)
- React/Vite Frontend (2 replicas, auto-scaling 2-5)
- Ingress Controller (AWS ALB)
- HorizontalPodAutoscaler (CPU/Memory based)

### Features
- ✅ Auto-scaling (HPA)
- ✅ Load balancing (ALB)
- ✅ Persistent storage (EBS)
- ✅ Health checks
- ✅ Rolling updates
- ✅ High availability (multi-AZ)
- ✅ Managed database backups

---

**Happy Deploying! 🚀**
