# Deploy LazySheeps to Kubernetes
# This script deploys all Kubernetes resources in the correct order

Write-Host "🚀 Deploying LazySheeps to Kubernetes" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create namespace
Write-Host "📦 Step 1: Creating namespace..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create namespace" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Namespace created!" -ForegroundColor Green
Write-Host ""

# Step 2: Create ConfigMap and Secrets
Write-Host "🔧 Step 2: Creating ConfigMap and Secrets..." -ForegroundColor Yellow
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create ConfigMap/Secrets" -ForegroundColor Red
    exit 1
}

Write-Host "✅ ConfigMap and Secrets created!" -ForegroundColor Green
Write-Host ""

# Step 3: Create StorageClass and PVC
Write-Host "💾 Step 3: Creating StorageClass and PVC..." -ForegroundColor Yellow
kubectl apply -f k8s/storageclass.yaml
kubectl apply -f k8s/postgres-pvc.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create StorageClass/PVC" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Storage resources created!" -ForegroundColor Green
Write-Host ""

# Step 4: Deploy PostgreSQL
Write-Host "🗄️  Step 4: Deploying PostgreSQL..." -ForegroundColor Yellow
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/postgres-service.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to deploy PostgreSQL" -ForegroundColor Red
    exit 1
}

Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Gray
kubectl wait --for=condition=ready pod -l app=postgres -n lazysheeps --timeout=300s

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  PostgreSQL took too long to start, but continuing..." -ForegroundColor Yellow
} else {
    Write-Host "✅ PostgreSQL is ready!" -ForegroundColor Green
}
Write-Host ""

# Step 5: Deploy Backend
Write-Host "🔧 Step 5: Deploying Backend..." -ForegroundColor Yellow
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to deploy Backend" -ForegroundColor Red
    exit 1
}

Write-Host "⏳ Waiting for Backend to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10
kubectl wait --for=condition=ready pod -l app=backend -n lazysheeps --timeout=300s

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Backend took too long to start, but continuing..." -ForegroundColor Yellow
} else {
    Write-Host "✅ Backend is ready!" -ForegroundColor Green
}
Write-Host ""

# Step 6: Run database migrations
Write-Host "📊 Step 6: Running database migrations..." -ForegroundColor Yellow
$backendPod = (kubectl get pods -n lazysheeps -l app=backend -o jsonpath='{.items[0].metadata.name}')

if ([string]::IsNullOrEmpty($backendPod)) {
    Write-Host "⚠️  No backend pod found. Skipping migrations." -ForegroundColor Yellow
} else {
    Write-Host "Running migrations on pod: $backendPod" -ForegroundColor Gray
    kubectl exec -it $backendPod -n lazysheeps -- python manage.py migrate
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations completed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Migrations may have failed, but continuing..." -ForegroundColor Yellow
    }
}
Write-Host ""

# Step 7: Deploy Frontend
Write-Host "🌐 Step 7: Deploying Frontend..." -ForegroundColor Yellow
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to deploy Frontend" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Frontend deployed!" -ForegroundColor Green
Write-Host ""

# Step 8: Create Ingress
Write-Host "🌍 Step 8: Creating Ingress..." -ForegroundColor Yellow
kubectl apply -f k8s/ingress.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create Ingress" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Ingress created!" -ForegroundColor Green
Write-Host ""

# Step 9: Create HorizontalPodAutoscalers
Write-Host "📈 Step 9: Creating HorizontalPodAutoscalers..." -ForegroundColor Yellow
kubectl apply -f k8s/hpa.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Failed to create HPA (metrics server may not be installed)" -ForegroundColor Yellow
} else {
    Write-Host "✅ HPA created!" -ForegroundColor Green
}
Write-Host ""

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get deployment status
Write-Host "📊 Deployment Status:" -ForegroundColor Yellow
kubectl get all -n lazysheeps
Write-Host ""

# Get Ingress URL
Write-Host "🌐 Getting Ingress URL..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$ingressHostname = (kubectl get ingress lazysheeps-ingress -n lazysheeps -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>$null)

if ([string]::IsNullOrEmpty($ingressHostname)) {
    Write-Host "⏳ Ingress is being provisioned... This may take 2-3 minutes." -ForegroundColor Gray
    Write-Host "Run this command to get the URL once ready:" -ForegroundColor Gray
    Write-Host "kubectl get ingress lazysheeps-ingress -n lazysheeps" -ForegroundColor White
} else {
    Write-Host "✅ Your application is available at:" -ForegroundColor Green
    Write-Host "http://$ingressHostname" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "View pods:      kubectl get pods -n lazysheeps" -ForegroundColor White
Write-Host "View logs:      kubectl logs -f deployment/backend -n lazysheeps" -ForegroundColor White
Write-Host "View services:  kubectl get svc -n lazysheeps" -ForegroundColor White
Write-Host "View ingress:   kubectl get ingress -n lazysheeps" -ForegroundColor White
Write-Host ""
