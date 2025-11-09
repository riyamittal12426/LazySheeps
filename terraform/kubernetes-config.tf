# Kubernetes Namespace
resource "kubernetes_namespace" "lazysheeps" {
  metadata {
    name = "lazysheeps"
    labels = {
      name        = "lazysheeps"
      environment = var.environment
    }
  }

  depends_on = [module.eks]
}

# ConfigMap
resource "kubernetes_config_map" "lazysheeps_config" {
  metadata {
    name      = "lazysheeps-config"
    namespace = kubernetes_namespace.lazysheeps.metadata[0].name
  }

  data = {
    ALLOWED_HOSTS          = "backend-service,localhost,127.0.0.1"
    CORS_ALLOWED_ORIGINS   = "http://localhost:5173,https://your-frontend-domain.com"
    POSTGRES_DB            = "lazysheeps_db"
    POSTGRES_USER          = "lazysheeps_user"
    DATABASE_HOST          = "postgres-service"
    DATABASE_PORT          = "5432"
    VITE_API_URL           = "http://backend-service:8000"
    VITE_WS_URL            = "ws://backend-service:8000"
  }
}

# Secrets
resource "kubernetes_secret" "lazysheeps_secret" {
  metadata {
    name      = "lazysheeps-secret"
    namespace = kubernetes_namespace.lazysheeps.metadata[0].name
  }

  type = "Opaque"

  data = {
    POSTGRES_PASSWORD    = base64encode(var.postgres_password)
    SECRET_KEY           = base64encode(var.django_secret_key)
    GITHUB_CLIENT_ID     = base64encode(var.github_client_id)
    GITHUB_CLIENT_SECRET = base64encode(var.github_client_secret)
  }
}

# Wait for EBS CSI driver to be ready
resource "time_sleep" "wait_for_ebs_csi" {
  depends_on = [aws_eks_addon.ebs_csi_driver]

  create_duration = "60s"
}

# StorageClass for EBS
resource "kubernetes_storage_class" "ebs_sc" {
  metadata {
    name = "ebs-sc"
  }

  storage_provisioner    = "ebs.csi.aws.com"
  reclaim_policy         = "Delete"
  allow_volume_expansion = true
  volume_binding_mode    = "WaitForFirstConsumer"

  parameters = {
    type       = "gp3"
    iops       = "3000"
    throughput = "125"
    encrypted  = "true"
  }

  depends_on = [time_sleep.wait_for_ebs_csi]
}

# PersistentVolumeClaim for PostgreSQL
# Note: This won't provision a volume until a pod claims it (WaitForFirstConsumer mode)
resource "kubernetes_persistent_volume_claim" "postgres_pvc" {
  metadata {
    name      = "postgres-pvc"
    namespace = kubernetes_namespace.lazysheeps.metadata[0].name
  }

  spec {
    access_modes       = ["ReadWriteOnce"]
    storage_class_name = kubernetes_storage_class.ebs_sc.metadata[0].name

    resources {
      requests = {
        storage = "10Gi"
      }
    }
  }

  wait_until_bound = false  # Don't wait for binding (happens when pod is scheduled)

  depends_on = [kubernetes_storage_class.ebs_sc]
}
