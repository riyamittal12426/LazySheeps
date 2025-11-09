# 🚀 GitHub CI/CD Pipeline Setup Guide

Complete guide for setting up automated CI/CD pipelines for LazySheeps deployment to AWS EKS.

## 📋 Overview

This repository includes 4 GitHub Actions workflows:

1. **CI/CD Pipeline** (`ci-cd-pipeline.yml`) - Main deployment pipeline
2. **Terraform Infrastructure** (`terraform-infrastructure.yml`) - Infrastructure provisioning
3. **Pull Request Validation** (`pr-validation.yml`) - Code quality checks on PRs
4. **Health Check** (`health-check.yml`) - Scheduled application monitoring

## 🔧 Setup Instructions

### Step 1: Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

#### Required Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | AWS IAM Console → Users → Security Credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | Same as above |

#### How to Create AWS Credentials

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click "Users" → "Create user"
3. User name: `github-actions-user`
4. Attach policies:
   - `AmazonEKSClusterPolicy`
   - `AmazonEKSWorkerNodePolicy`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonEKS_CNI_Policy`
   - `AmazonEBSCSIDriverPolicy`
   - `ElasticLoadBalancingFullAccess`
   - Or create custom policy (see below)
5. Click "Security credentials" → "Create access key"
6. Choose "Application running outside AWS"
7. Copy the Access Key ID and Secret Access Key

#### Minimal IAM Policy for GitHub Actions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:*",
        "ec2:*",
        "ecr:*",
        "iam:*",
        "elasticloadbalancing:*",
        "autoscaling:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Step 2: Update Kubernetes Secrets

Before deploying, update `k8s/secret.yaml` with base64-encoded values:

```bash
# Generate base64 values (Linux/Mac/Git Bash)
echo -n 'your-postgres-password' | base64
echo -n 'your-django-secret-key' | base64

# PowerShell
$text = "your-postgres-password"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
[Convert]::ToBase64String($bytes)
```

Update these secrets in `k8s/secret.yaml`:
- `POSTGRES_PASSWORD`
- `SECRET_KEY`
- `GITHUB_CLIENT_ID` (optional)
- `GITHUB_CLIENT_SECRET` (optional)

### Step 3: Commit and Push Secrets

```bash
git add k8s/secret.yaml
git commit -m "Update Kubernetes secrets"
git push origin main
```

**⚠️ IMPORTANT:** Make sure `k8s/secret.yaml` is in `.gitignore` if it contains real secrets. For production, use AWS Secrets Manager or External Secrets Operator.

## 🎯 Workflows Explained

### 1. CI/CD Pipeline (`ci-cd-pipeline.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**What it does:**

#### On Pull Requests:
1. ✅ Runs backend tests (Python, Django)
2. ✅ Runs frontend tests (Node.js, React)
3. ✅ Lints code (flake8, ESLint)
4. ✅ Builds applications to ensure no errors

#### On Push to `main`:
1. ✅ All of the above
2. ✅ Builds Docker images
3. ✅ Pushes images to AWS ECR
4. ✅ Deploys to EKS cluster
5. ✅ Runs database migrations
6. ✅ Verifies deployment

**Jobs:**
- `backend-tests` - Tests Django backend with PostgreSQL
- `frontend-tests` - Tests React frontend
- `build-and-push` - Builds and pushes to ECR
- `deploy-to-eks` - Deploys to Kubernetes

### 2. Terraform Infrastructure (`terraform-infrastructure.yml`)

**Triggers:**
- Manual workflow dispatch only

**What it does:**
- Provisions AWS EKS infrastructure using Terraform
- Can `plan`, `apply`, or `destroy` infrastructure

**Usage:**
1. Go to Actions tab in GitHub
2. Select "Terraform Infrastructure"
3. Click "Run workflow"
4. Choose action: `plan`, `apply`, or `destroy`

**Actions:**
- `plan` - Shows what will be created/changed
- `apply` - Creates/updates infrastructure
- `destroy` - Deletes all infrastructure

### 3. Pull Request Validation (`pr-validation.yml`)

**Triggers:**
- Pull requests to `main` or `develop`

**What it does:**
1. ✅ Validates commit messages
2. ✅ Checks code quality (backend & frontend)
3. ✅ Runs security scans with Trivy
4. ✅ Validates file changes

**Jobs:**
- `validate` - General PR validation
- `backend-check` - Python code quality
- `frontend-check` - JavaScript/React code quality
- `security-scan` - Vulnerability scanning

### 4. Health Check (`health-check.yml`)

**Triggers:**
- Scheduled: Every hour
- Manual workflow dispatch

**What it does:**
1. ✅ Checks pod status
2. ✅ Monitors pod restarts
3. ✅ Checks resource usage
4. ✅ Verifies HPA status
5. ✅ Tests application endpoints
6. ✅ Sends notifications on failure

## 🚀 Usage Guide

### First Time Deployment

1. **Create EKS cluster using Terraform:**
   ```bash
   # Go to GitHub → Actions → Terraform Infrastructure
   # Run workflow → Select "apply"
   ```
   ⏱️ Takes ~15-20 minutes

2. **Deploy application:**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push origin main
   ```
   The CI/CD pipeline will automatically:
   - Run tests
   - Build Docker images
   - Push to ECR
   - Deploy to EKS

3. **Get application URL:**
   - Check Actions logs for the URL
   - Or run: `kubectl get ingress lazysheeps-ingress -n lazysheeps`

### Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make your changes**

3. **Create Pull Request:**
   ```bash
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```
   
   - PR validation will run automatically
   - Tests and linting must pass

4. **Merge to main:**
   - Once PR is approved and merged
   - CI/CD pipeline deploys automatically

### Rollback

If a deployment fails:

1. **Revert the commit:**
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Or deploy a specific version:**
   ```bash
   # Update image tags in k8s/*.yaml to previous version
   git add k8s/
   git commit -m "Rollback to previous version"
   git push origin main
   ```

## 📊 Monitoring

### View Deployment Status

1. Go to **Actions** tab in GitHub
2. Click on the latest workflow run
3. View logs for each job

### Check Application Health

1. Go to **Actions** → **Health Check**
2. Click "Run workflow" for manual health check
3. Or wait for scheduled hourly checks

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -n lazysheeps

# Frontend logs
kubectl logs -f deployment/frontend -n lazysheeps

# All pods
kubectl get pods -n lazysheeps
```

## 🔐 Security Best Practices

### 1. Never Commit Real Secrets

Add to `.gitignore`:
```gitignore
k8s/secret.yaml
.env
*.pem
*.key
```

### 2. Use External Secrets

For production, use:
- **AWS Secrets Manager** integration
- **External Secrets Operator**
- **Sealed Secrets**

### 3. Rotate Credentials

- Rotate AWS credentials every 90 days
- Rotate database passwords regularly
- Rotate Django SECRET_KEY on security incidents

### 4. Enable Branch Protection

Repository Settings → Branches → Add rule:
- Require pull request reviews
- Require status checks to pass
- Require conversation resolution

## 🐛 Troubleshooting

### Pipeline Fails on Tests

```bash
# Run tests locally first
cd backend
python manage.py test

cd frontend
npm test
```

### ECR Push Fails

- Check AWS credentials are correct
- Verify ECR repositories exist
- Check IAM permissions

### Deployment Fails

```bash
# Check pod status
kubectl get pods -n lazysheeps

# View pod logs
kubectl logs <pod-name> -n lazysheeps

# Describe pod for events
kubectl describe pod <pod-name> -n lazysheeps
```

### Ingress Not Getting URL

- Wait 2-3 minutes for Load Balancer provisioning
- Check ALB controller logs:
  ```bash
  kubectl logs -n kube-system deployment/aws-load-balancer-controller
  ```

## 💰 Cost Management

### GitHub Actions Usage

- **Free tier:** 2,000 minutes/month for private repos
- **Public repos:** Unlimited

### AWS Costs

With CI/CD, you're only charged for:
- EKS cluster running time
- EC2 instances
- Data transfer
- ECR storage

**Estimated costs:**
- **Development:** ~$5-10/day if kept running
- **Scheduled deployments:** Deploy only during business hours to save costs

### Cost Optimization

1. **Auto-scaling:**
   - HPA scales down during low traffic
   - Cluster Autoscaler reduces nodes

2. **Scheduled shutdowns:**
   - Stop cluster outside business hours
   - Use spot instances for non-prod

3. **Delete unused resources:**
   ```bash
   # Run Terraform destroy when not needed
   # Go to Actions → Terraform Infrastructure → destroy
   ```

## 📈 Advanced Features

### Add Slack Notifications

Update workflow to add Slack notifications:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Add Email Notifications

GitHub automatically sends emails on:
- Workflow failures
- Deployment failures

Configure in: Settings → Notifications

### Blue-Green Deployment

For zero-downtime deployments:

1. Create blue/green deployments
2. Use weighted routing in Ingress
3. Gradual traffic shift

### Canary Deployments

1. Deploy new version to small percentage
2. Monitor metrics
3. Gradually increase traffic

## 📝 Workflow Customization

### Change Deployment Branch

Edit `.github/workflows/ci-cd-pipeline.yml`:

```yaml
on:
  push:
    branches:
      - main        # Change this
      - production  # Or add more branches
```

### Add More Tests

Add to `backend-tests` or `frontend-tests` jobs:

```yaml
- name: Run integration tests
  run: |
    npm run test:integration
```

### Change Schedule

Edit `.github/workflows/health-check.yml`:

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours instead of 1
```

## 🎓 Learning Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## ✅ Checklist

Before going live:

- [ ] AWS credentials configured in GitHub Secrets
- [ ] Kubernetes secrets updated with real values
- [ ] Branch protection rules enabled
- [ ] EKS cluster created via Terraform
- [ ] First deployment successful
- [ ] Application URL accessible
- [ ] Health checks passing
- [ ] Monitoring set up
- [ ] Team notified of deployment URLs
- [ ] Documentation updated

---

**Ready to deploy?** Push to `main` branch and watch the magic happen! 🚀
