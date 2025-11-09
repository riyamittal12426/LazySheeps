# AWS EKS Deployment Guide for LazySheeps

This guide will help you deploy the LazySheeps application to AWS EKS (Elastic Kubernetes Service).

## Prerequisites

### Required Tools
- AWS CLI (v2 or later)
- kubectl (v1.27 or later)
- eksctl (for EKS cluster creation)
- Docker (for building images)
- AWS account with appropriate permissions

### Install Required Tools

```bash
# Install AWS CLI
# Windows (PowerShell)
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Install kubectl
curl -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"

# Install eksctl
choco install eksctl
# OR download from: https://github.com/weksctl-io/eksctl/releases
```

## Step 1: Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter output format (json)
```

## Step 2: Create EKS Cluster

### Option A: Using eksctl (Recommended)

```bash
# Create cluster with managed node group
eksctl create cluster \
  --name lazysheeps-cluster \
  --region us-east-1 \
  --nodegroup-name lazysheeps-nodes \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed
```

This will take 15-20 minutes to complete.

### Option B: Using AWS Console
1. Go to AWS EKS Console
2. Click "Create Cluster"
3. Configure cluster settings
4. Create node group with t3.medium instances

## Step 3: Configure kubectl

```bash
# Update kubeconfig to connect to your cluster
aws eks update-kubeconfig --region us-east-1 --name lazysheeps-cluster

# Verify connection
kubectl get nodes
```

## Step 4: Install AWS Load Balancer Controller

The ALB Ingress Controller is required for the Ingress resource to work.

### Install using Helm

```bash
# Add helm repo
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Create IAM policy (download policy document first)
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.6.0/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# Create service account
eksctl create iamserviceaccount \
  --cluster=lazysheeps-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::<ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --approve

# Install the controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=lazysheeps-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

## Step 5: Install EBS CSI Driver

Required for persistent volumes (PostgreSQL storage).

```bash
# Create IAM service account for EBS CSI driver
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster lazysheeps-cluster \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve \
  --role-only \
  --role-name AmazonEKS_EBS_CSI_DriverRole

# Install EBS CSI driver addon
aws eks create-addon \
  --cluster-name lazysheeps-cluster \
  --addon-name aws-ebs-csi-driver \
  --service-account-role-arn arn:aws:iam::<ACCOUNT_ID>:role/AmazonEKS_EBS_CSI_DriverRole
```

## Step 6: Build and Push Docker Images

### Setup AWS ECR (Elastic Container Registry)

```bash
# Create ECR repositories
aws ecr create-repository --repository-name lazysheeps-backend --region us-east-1
aws ecr create-repository --repository-name lazysheeps-frontend --region us-east-1

# Get login password and authenticate Docker
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

### Build and Push Backend

```bash
cd backend

# Build image
docker build -t lazysheeps-backend:latest .

# Tag image
docker tag lazysheeps-backend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-backend:latest

# Push image
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-backend:latest
```

### Build and Push Frontend

```bash
cd frontend

# Build image
docker build -t lazysheeps-frontend:latest .

# Tag image
docker tag lazysheeps-frontend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-frontend:latest

# Push image
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-frontend:latest
```

## Step 7: Configure Kubernetes Secrets

### Generate Base64 Encoded Values

```bash
# Windows PowerShell
$text = "your-postgres-password"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
[Convert]::ToBase64String($bytes)

# Repeat for SECRET_KEY and other secrets
```

### Update secret.yaml

Edit `k8s/secret.yaml` and replace the placeholder values with your actual base64-encoded secrets:
- `POSTGRES_PASSWORD`
- `SECRET_KEY` (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `GITHUB_CLIENT_ID` (if using GitHub OAuth)
- `GITHUB_CLIENT_SECRET` (if using GitHub OAuth)

## Step 8: Update ConfigMap and Deployments

### Update ConfigMap (k8s/configmap.yaml)
- Update `CORS_ALLOWED_ORIGINS` with your actual domain
- Update `VITE_API_URL` if using custom domain

### Update Deployments
- In `k8s/backend-deployment.yaml`, replace `your-registry` with your ECR URL:
  ```yaml
  image: <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-backend:latest
  ```
- In `k8s/frontend-deployment.yaml`, replace `your-registry` with your ECR URL:
  ```yaml
  image: <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-frontend:latest
  ```

### Update Ingress (k8s/ingress.yaml)
- Replace `your-domain.com` with your actual domain
- If using HTTPS, uncomment and add your ACM certificate ARN

## Step 9: Deploy to Kubernetes

Deploy in the following order:

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create ConfigMap and Secrets
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# 3. Create StorageClass and PVC
kubectl apply -f k8s/storageclass.yaml
kubectl apply -f k8s/postgres-pvc.yaml

# 4. Deploy PostgreSQL
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/postgres-service.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n lazysheeps --timeout=300s

# 5. Deploy Backend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# Wait for backend to be ready
kubectl wait --for=condition=ready pod -l app=backend -n lazysheeps --timeout=300s

# 6. Deploy Frontend
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 7. Create Ingress
kubectl apply -f k8s/ingress.yaml

# 8. Create HorizontalPodAutoscalers
kubectl apply -f k8s/hpa.yaml
```

### Or Deploy All at Once (after verification)

```bash
kubectl apply -f k8s/
```

## Step 10: Run Database Migrations

```bash
# Get backend pod name
kubectl get pods -n lazysheeps -l app=backend

# Run migrations
kubectl exec -it <backend-pod-name> -n lazysheeps -- python manage.py migrate

# Create superuser (optional)
kubectl exec -it <backend-pod-name> -n lazysheeps -- python manage.py createsuperuser
```

## Step 11: Verify Deployment

```bash
# Check all resources
kubectl get all -n lazysheeps

# Check pods status
kubectl get pods -n lazysheeps

# Check services
kubectl get svc -n lazysheeps

# Check ingress
kubectl get ingress -n lazysheeps

# Get ALB URL
kubectl get ingress lazysheeps-ingress -n lazysheeps -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# View logs
kubectl logs -f deployment/backend -n lazysheeps
kubectl logs -f deployment/frontend -n lazysheeps
```

## Step 12: Configure DNS (Optional)

1. Get the ALB DNS name from Step 11
2. Go to your DNS provider (Route 53, Cloudflare, etc.)
3. Create a CNAME record pointing your domain to the ALB DNS name

### Using AWS Route 53

```bash
# Create hosted zone (if not exists)
aws route53 create-hosted-zone --name your-domain.com --caller-reference $(date +%s)

# Get ALB DNS
ALB_DNS=$(kubectl get ingress lazysheeps-ingress -n lazysheeps -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Create DNS record (you'll need to create a JSON file for this)
# See AWS Route 53 documentation for details
```

## Step 13: Setup HTTPS with ACM (Optional but Recommended)

### Request SSL Certificate

```bash
# Request certificate
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS \
  --region us-east-1

# Get certificate ARN
aws acm list-certificates --region us-east-1
```

### Update Ingress

Uncomment and update the certificate ARN in `k8s/ingress.yaml`:
```yaml
alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:<ACCOUNT_ID>:certificate/<CERT_ID>
```

Then reapply:
```bash
kubectl apply -f k8s/ingress.yaml
```

## Monitoring and Management

### View Pod Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -n lazysheeps

# Frontend logs
kubectl logs -f deployment/frontend -n lazysheeps

# PostgreSQL logs
kubectl logs -f statefulset/postgres -n lazysheeps
```

### Scale Deployments Manually

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n lazysheeps

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n lazysheeps
```

### Check HPA Status

```bash
kubectl get hpa -n lazysheeps

# Detailed view
kubectl describe hpa backend-hpa -n lazysheeps
kubectl describe hpa frontend-hpa -n lazysheeps
```

### Update Application

```bash
# Build and push new image
docker build -t lazysheeps-backend:v2 ./backend
docker tag lazysheeps-backend:v2 <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-backend:v2
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-backend:v2

# Update deployment
kubectl set image deployment/backend backend=<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lazysheeps-backend:v2 -n lazysheeps

# Check rollout status
kubectl rollout status deployment/backend -n lazysheeps
```

### Rollback Deployment

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n lazysheeps

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n lazysheeps
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name> -n lazysheeps

# Check logs
kubectl logs <pod-name> -n lazysheeps
```

### Database Connection Issues

```bash
# Test database connection from backend pod
kubectl exec -it <backend-pod-name> -n lazysheeps -- bash
python manage.py dbshell
```

### Ingress Not Working

```bash
# Check ingress events
kubectl describe ingress lazysheeps-ingress -n lazysheeps

# Check ALB controller logs
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

### PVC Not Binding

```bash
# Check PVC status
kubectl describe pvc postgres-pvc -n lazysheeps

# Check EBS CSI driver
kubectl get pods -n kube-system | grep ebs-csi
```

## Cost Optimization

### Use Spot Instances for Non-Critical Workloads

```bash
eksctl create nodegroup \
  --cluster lazysheeps-cluster \
  --name spot-nodes \
  --spot \
  --instance-types t3.medium,t3a.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 4
```

### Enable Cluster Autoscaler

```bash
# Install cluster autoscaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

# Edit deployment to add cluster name
kubectl -n kube-system edit deployment cluster-autoscaler
# Add: --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/lazysheeps-cluster
```

## Cleanup

To delete all resources:

```bash
# Delete Kubernetes resources
kubectl delete -f k8s/

# Delete namespace
kubectl delete namespace lazysheeps

# Delete EKS cluster
eksctl delete cluster --name lazysheeps-cluster --region us-east-1

# Delete ECR repositories
aws ecr delete-repository --repository-name lazysheeps-backend --force
aws ecr delete-repository --repository-name lazysheeps-frontend --force
```

## Security Best Practices

1. **Use Secrets Management**: Consider AWS Secrets Manager or Parameter Store instead of Kubernetes Secrets
2. **Enable Network Policies**: Restrict pod-to-pod communication
3. **Use Pod Security Policies**: Enforce security standards
4. **Enable Audit Logging**: Track all API server requests
5. **Regular Updates**: Keep EKS version and node images up to date
6. **IAM Roles**: Use IAM roles for service accounts (IRSA) for fine-grained permissions
7. **Encrypt at Rest**: Enable encryption for EBS volumes and RDS if used

## Additional Resources

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [EBS CSI Driver](https://github.com/kubernetes-sigs/aws-ebs-csi-driver)

## Support

For issues with:
- EKS cluster: Check AWS CloudWatch logs
- Application: Check pod logs with `kubectl logs`
- ALB: Check ALB controller logs in kube-system namespace
