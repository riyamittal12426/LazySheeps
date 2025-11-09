# 🚀 LazySheeps - Terraform AWS EKS Deployment

Complete **Infrastructure as Code** solution for deploying LazySheeps to AWS EKS using Terraform.

## 🎯 Why Terraform?

✅ **Declarative** - Define infrastructure in code  
✅ **Reproducible** - Create identical environments  
✅ **Version Control** - Track infrastructure changes  
✅ **State Management** - Automatic resource tracking  
✅ **Modular** - Reusable components  
✅ **Best Practices** - Industry-standard approach  

## 💰 Cost Estimate

### Testing (1-2 hours): **~$1-2**
- EKS Control Plane: $0.20
- EC2 Nodes (2× t3.medium): $0.16
- Load Balancer: $0.05
- EBS Storage: <$0.01

### Monthly (if kept running): **~$150-300**
- EKS Control Plane: $72/month
- EC2 Nodes: $60-120/month  
- Load Balancer: $16/month
- Storage & Data Transfer: ~$5/month

## 📋 Prerequisites

### Required Software
- ✅ **Terraform** >= 1.0
- ✅ **AWS CLI** (already installed)
- ✅ **Docker Desktop** (already installed)
- ✅ **kubectl** (already installed)
- ✅ **AWS Account** with permissions

### Install Terraform

```powershell
# Using Chocolatey
choco install terraform -y

# OR download from
# https://www.terraform.io/downloads
```

Verify installation:
```powershell
terraform version
```

## 🏗️ What Gets Created

### AWS Infrastructure
- **VPC** with public/private subnets across 3 AZs
- **EKS Cluster** (managed control plane)
- **Managed Node Group** (2-4 t3.medium instances)
- **NAT Gateway** for private subnet internet access
- **Security Groups** with proper ingress/egress rules
- **IAM Roles** for EKS, nodes, and service accounts
- **ECR Repositories** for backend and frontend images
- **EBS CSI Driver** for persistent volumes
- **AWS Load Balancer Controller** for Ingress

### Kubernetes Resources
- **Namespace** (lazysheeps)
- **ConfigMap** (non-sensitive configuration)
- **Secrets** (passwords, keys)
- **StorageClass** (EBS gp3 with encryption)
- **PersistentVolumeClaim** (10Gi for PostgreSQL)
- **StatefulSet** (PostgreSQL with persistent storage)
- **Deployments** (Backend × 3, Frontend × 2)
- **Services** (ClusterIP for internal, LoadBalancer for external)
- **Health Checks** (liveness and readiness probes)
- **Resource Limits** (CPU and memory constraints)

## 🚀 Quick Start (3 Commands!)

### 1. Deploy Infrastructure

```powershell
.\terraform-deploy.ps1
```

This will:
- Initialize Terraform
- Create execution plan
- Deploy all AWS resources (~15-20 minutes)
- Output ECR URLs and cluster info

### 2. Build and Push Docker Images

```powershell
.\terraform-build-push.ps1
```

This will:
- Login to ECR
- Build backend and frontend images
- Push images to ECR repositories
- Kubernetes will automatically pull and deploy

### 3. Access Your Application

```powershell
# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name lazysheeps-cluster

# Get frontend URL
kubectl get svc frontend-service -n lazysheeps

# Wait 2-3 minutes for LoadBalancer provisioning, then access the URL
```

**That's it! Your application is live! 🎉**

## 📁 Terraform File Structure

```
terraform/
├── providers.tf          # Provider configurations (AWS, Kubernetes, Helm)
├── variables.tf          # Input variables with defaults
├── terraform.tfvars      # Your actual values (customize this!)
├── data.tf              # Data sources (AWS account info)
├── vpc.tf               # VPC, subnets, NAT gateway
├── eks.tf               # EKS cluster, node groups, addons
├── ecr.tf               # ECR repositories with lifecycle policies
├── kubernetes-config.tf  # Namespace, ConfigMap, Secrets, Storage
├── kubernetes-postgres.tf # PostgreSQL StatefulSet and Service
├── kubernetes-apps.tf    # Backend and Frontend deployments
└── outputs.tf           # Output values (URLs, commands)
```

## ⚙️ Configuration

### Edit `terraform/terraform.tfvars`

```hcl
# Change these values before deploying!

postgres_password = "your-secure-password-here"
django_secret_key = "your-long-random-secret-key-here"

# Optional GitHub OAuth
github_client_id     = "your-github-client-id"
github_client_secret = "your-github-client-secret"

# Customize cluster size
node_desired_size = 2  # Change to 3 or 4 for more capacity
node_instance_type = "t3.medium"  # Or t3.large for better performance
```

### Available Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aws_region` | `us-east-1` | AWS region |
| `cluster_name` | `lazysheeps-cluster` | EKS cluster name |
| `cluster_version` | `1.28` | Kubernetes version |
| `node_instance_type` | `t3.medium` | EC2 instance type |
| `node_desired_size` | `2` | Initial node count |
| `node_min_size` | `2` | Minimum nodes |
| `node_max_size` | `4` | Maximum nodes |
| `postgres_password` | (required) | Database password |
| `django_secret_key` | (required) | Django secret |

## 📊 Managing Your Deployment

### View Resources

```powershell
# Terraform resources
cd terraform
terraform show

# Kubernetes resources
kubectl get all -n lazysheeps

# Check pod status
kubectl get pods -n lazysheeps

# View logs
kubectl logs -f deployment/backend -n lazysheeps
kubectl logs -f deployment/frontend -n lazysheeps
```

### Update Application

```powershell
# Make code changes, then rebuild and push
.\terraform-build-push.ps1

# Restart deployments to pull new images
kubectl rollout restart deployment/backend -n lazysheeps
kubectl rollout restart deployment/frontend -n lazysheeps

# Monitor rollout
kubectl rollout status deployment/backend -n lazysheeps
```

### Scale Deployments

```powershell
# Scale backend
kubectl scale deployment backend --replicas=5 -n lazysheeps

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n lazysheeps

# Or edit terraform/kubernetes-apps.tf and re-apply
cd terraform
terraform apply
```

### Run Database Migrations

```powershell
# Get backend pod name
$POD = (kubectl get pods -n lazysheeps -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -it $POD -n lazysheeps -- python manage.py migrate

# Create superuser
kubectl exec -it $POD -n lazysheeps -- python manage.py createsuperuser
```

## 🔧 Terraform Commands

### View Plan

```powershell
cd terraform
terraform plan
```

### Apply Changes

```powershell
cd terraform
terraform apply
```

### View Current State

```powershell
cd terraform
terraform show
```

### View Outputs

```powershell
cd terraform
terraform output

# Specific output
terraform output frontend_service_url
```

### Format Code

```powershell
cd terraform
terraform fmt -recursive
```

### Validate Configuration

```powershell
cd terraform
terraform validate
```

## 🧹 Cleanup (Delete Everything)

**Important:** Run this after testing to avoid ongoing charges!

```powershell
cd terraform
terraform destroy
```

This will:
- Delete all Kubernetes resources
- Delete EKS cluster and nodes
- Delete VPC, subnets, NAT gateway
- Delete ECR repositories and images
- Delete IAM roles and policies
- Remove all AWS resources

**Verification:**
Check AWS Console to ensure:
- EC2 Dashboard → No instances or load balancers
- EKS Dashboard → No clusters
- ECR Dashboard → No repositories
- VPC Dashboard → Default VPC only

## 🔍 Troubleshooting

### Terraform Init Fails

```powershell
# Clear cache and retry
Remove-Item -Recurse -Force terraform/.terraform
cd terraform
terraform init
```

### EKS Cluster Creation Timeout

```powershell
# Check CloudFormation stacks
aws cloudformation describe-stacks --region us-east-1

# If stuck, manually delete stack and retry
```

### Pods Not Starting

```powershell
# Describe pod
kubectl describe pod <pod-name> -n lazysheeps

# Check events
kubectl get events -n lazysheeps --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n lazysheeps
```

### Images Not Pulling

```powershell
# Verify images exist in ECR
aws ecr list-images --repository-name lazysheeps-backend
aws ecr list-images --repository-name lazysheeps-frontend

# Check node IAM role has ECR permissions
cd terraform
terraform output
```

### LoadBalancer Stuck Pending

```powershell
# Check AWS Load Balancer Controller
kubectl logs -n kube-system deployment/aws-load-balancer-controller

# Verify service
kubectl describe svc frontend-service -n lazysheeps
```

### Database Connection Issues

```powershell
# Check PostgreSQL pod
kubectl get pods -n lazysheeps -l app=postgres

# Check logs
kubectl logs -f statefulset/postgres -n lazysheeps

# Test connection from backend
kubectl exec -it <backend-pod> -n lazysheeps -- python manage.py dbshell
```

## 🔐 Security Best Practices

1. **Change Default Passwords**: Update `terraform.tfvars` with strong passwords
2. **Enable Encryption**: EBS volumes are encrypted by default
3. **Use Secrets Manager**: For production, use AWS Secrets Manager
4. **Network Policies**: Consider adding Kubernetes NetworkPolicies
5. **Update Regularly**: Keep Terraform providers and modules updated
6. **State File Security**: Store Terraform state in S3 with encryption
7. **Least Privilege**: Review IAM roles and remove unnecessary permissions

## 📈 Production Recommendations

### For Production Use:

1. **Remote State Backend**:
```hcl
# Add to providers.tf
terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "lazysheeps/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}
```

2. **Use RDS Instead of PostgreSQL Pod**:
```hcl
# Add RDS module to terraform/
module "db" {
  source = "terraform-aws-modules/rds/aws"
  # Configuration
}
```

3. **Add Auto-Scaling**:
```hcl
# Add HPA resources to kubernetes-apps.tf
resource "kubernetes_horizontal_pod_autoscaler" "backend" {
  # Configuration
}
```

4. **Setup Monitoring**:
- CloudWatch Container Insights
- Prometheus + Grafana
- AWS X-Ray for tracing

5. **CI/CD Pipeline**:
- GitHub Actions / GitLab CI
- Automatic image builds
- Terraform Cloud for state management

## 📚 Additional Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

## 🆘 Support

### Common Issues

| Issue | Solution |
|-------|----------|
| "Error: Kubernetes cluster unreachable" | Run `aws eks update-kubeconfig` |
| "Error: timeout waiting for load balancer" | Wait 5 minutes, LoadBalancer takes time |
| "Error: repository does not exist" | Run `terraform-deploy.ps1` first |
| "Error: insufficient capacity" | Change region or instance type |

### Getting Help

1. Check logs: `kubectl logs -f deployment/backend -n lazysheeps`
2. Check events: `kubectl get events -n lazysheeps`
3. Check Terraform: `cd terraform ; terraform show`
4. Check AWS Console (CloudWatch, EKS, EC2)

## ✨ Features

✅ **Infrastructure as Code** - Version-controlled infrastructure  
✅ **Automatic SSL** - AWS Load Balancer Controller  
✅ **Persistent Storage** - EBS volumes for database  
✅ **High Availability** - Multi-AZ deployment  
✅ **Auto-Scaling** - Cluster Autoscaler ready  
✅ **Security** - Encrypted volumes, private subnets  
✅ **Cost-Optimized** - Managed node groups, spot instances ready  
✅ **Production-Ready** - Health checks, resource limits  
✅ **Easy Cleanup** - One command to destroy everything  

---

**Happy Deploying with Terraform! 🚀**
