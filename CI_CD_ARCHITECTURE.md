# CI/CD Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                             │
│                         (LazySheeps)                                 │
└───────────┬─────────────────────────────────────────────┬───────────┘
            │                                             │
            │ Push to main                                │ Pull Request
            │                                             │
            v                                             v
┌───────────────────────────────┐           ┌──────────────────────────┐
│   CI/CD Pipeline Workflow     │           │  PR Validation Workflow  │
│   (ci-cd-pipeline.yml)        │           │  (pr-validation.yml)     │
└───────────┬───────────────────┘           └──────────┬───────────────┘
            │                                          │
            │ 1. Backend Tests                         │ 1. Code Quality
            │ 2. Frontend Tests                        │ 2. Security Scan
            │ 3. Build Docker Images                   │ 3. Lint Check
            │ 4. Push to ECR                           └──────────────────
            │ 5. Deploy to EKS
            │
            v
┌───────────────────────────────────────────────────────────────────────┐
│                           AWS Cloud                                    │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    Amazon ECR                                    │ │
│  │  ┌──────────────────┐         ┌──────────────────┐             │ │
│  │  │ Backend Image    │         │ Frontend Image   │             │ │
│  │  │ (Django)         │         │ (React/Vite)     │             │ │
│  │  └──────────────────┘         └──────────────────┘             │ │
│  └──────────────┬────────────────────────────────────────────────┬─┘ │
│                 │                                                 │   │
│                 v                                                 v   │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                     Amazon EKS Cluster                           │ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────────┐ │ │
│  │  │              Kubernetes Namespace: lazysheeps              │ │ │
│  │  │                                                            │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │ │
│  │  │  │  PostgreSQL  │  │   Backend    │  │   Frontend   │   │ │ │
│  │  │  │  StatefulSet │  │  Deployment  │  │  Deployment  │   │ │ │
│  │  │  │   (1 pod)    │  │  (3 pods)    │  │  (2 pods)    │   │ │ │
│  │  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │ │ │
│  │  │         │                  │                  │           │ │ │
│  │  │         v                  v                  v           │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │ │
│  │  │  │ DB Service   │  │Backend Svc   │  │Frontend Svc  │   │ │ │
│  │  │  │ (ClusterIP)  │  │ (ClusterIP)  │  │(LoadBalancer)│   │ │ │
│  │  │  └──────────────┘  └──────────────┘  └──────┬───────┘   │ │ │
│  │  │                                               │           │ │ │
│  │  │  ┌─────────────────────────────────────────┐ │           │ │ │
│  │  │  │    HorizontalPodAutoscaler (HPA)        │ │           │ │ │
│  │  │  │  Backend: 2-10 pods | Frontend: 2-5     │ │           │ │ │
│  │  │  └─────────────────────────────────────────┘ │           │ │ │
│  │  │                                               │           │ │ │
│  │  │  ┌─────────────────────────────────────────┐ │           │ │ │
│  │  │  │            Ingress                       │ │           │ │ │
│  │  │  │  (AWS Application Load Balancer)        │◄┘           │ │ │
│  │  │  └──────────────────┬──────────────────────┘             │ │ │
│  │  └────────────────────┼────────────────────────────────────┘ │ │
│  └───────────────────────┼──────────────────────────────────────┘ │
│                          │                                         │
│  ┌───────────────────────▼──────────────────────────────────────┐ │
│  │              Amazon EBS (Persistent Storage)                 │ │
│  │                    PostgreSQL Data (10GB)                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             v
                    ┌────────────────┐
                    │   End Users    │
                    │  (Web Browser) │
                    └────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Scheduled Monitoring                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          Health Check Workflow (Every Hour)                  │  │
│  │  - Check pod status                                          │  │
│  │  - Monitor restarts                                          │  │
│  │  - Test endpoints                                            │  │
│  │  - Send alerts on failure                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Infrastructure Provisioning                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │      Terraform Infrastructure Workflow (Manual)              │  │
│  │  - terraform plan: Preview changes                           │  │
│  │  - terraform apply: Create/update infrastructure             │  │
│  │  - terraform destroy: Delete all resources                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Deployment Flow

```
Developer                GitHub Actions              AWS EKS
   │                           │                        │
   │  git push origin main     │                        │
   ├──────────────────────────>│                        │
   │                           │                        │
   │                    Run Tests & Build              │
   │                           │                        │
   │                    Build Docker Images            │
   │                           │                        │
   │                    Push to ECR                    │
   │                           ├───────────────────────>│
   │                           │                        │
   │                    Update Kubernetes              │
   │                           ├───────────────────────>│
   │                           │                        │
   │                           │         Deploy Pods    │
   │                           │         Run Migrations │
   │                           │         Health Checks  │
   │                           │                        │
   │     Deployment Complete   │                        │
   │<──────────────────────────┤                        │
   │                           │                        │
   │                    Application Live               │
   │<──────────────────────────────────────────────────┤
```

## Features

### ✅ Continuous Integration
- Automated testing on every commit
- Code quality checks (flake8, ESLint)
- Security vulnerability scanning
- Build validation

### ✅ Continuous Deployment
- Automatic deployment to EKS on main branch
- Zero-downtime rolling updates
- Automatic database migrations
- Health verification after deployment

### ✅ Auto-Scaling
- HorizontalPodAutoscaler for backend (2-10 pods)
- HorizontalPodAutoscaler for frontend (2-5 pods)
- CPU and memory-based scaling

### ✅ High Availability
- Multi-pod deployments
- Load balancing with ALB
- Health checks and automatic restarts
- Persistent storage for database

### ✅ Monitoring
- Scheduled health checks
- Pod status monitoring
- Resource usage tracking
- Automatic alerting on failures

## Cost Optimization

```
┌────────────────────────────────────────────────────┐
│  Cost Breakdown (Running 24/7)                     │
├────────────────────────────────────────────────────┤
│  EKS Control Plane:        $72/month               │
│  EC2 Nodes (2x t3.medium): $60/month               │
│  Load Balancer:            $16/month               │
│  EBS Storage (10GB):       $1/month                │
│  Data Transfer:            $5-10/month             │
├────────────────────────────────────────────────────┤
│  Total:                    ~$150-160/month         │
└────────────────────────────────────────────────────┘

With Auto-Scaling:
- Low traffic periods: Scales down to minimum pods
- High traffic periods: Scales up to maximum pods
- Average cost: ~$100-120/month
```

## Security Features

```
┌────────────────────────────────────────────────────┐
│  Security Measures                                 │
├────────────────────────────────────────────────────┤
│  ✅ Kubernetes Secrets for sensitive data          │
│  ✅ IAM roles for service accounts                 │
│  ✅ Network policies for pod isolation             │
│  ✅ Security scanning with Trivy                   │
│  ✅ Private ECR repositories                       │
│  ✅ HTTPS with AWS ALB                             │
│  ✅ Database credentials in secrets                │
│  ✅ No hardcoded passwords in code                 │
└────────────────────────────────────────────────────┘
```
