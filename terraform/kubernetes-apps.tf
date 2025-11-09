# Backend Deployment
resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.lazysheeps.metadata[0].name
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "backend"
        }
      }

      spec {
        init_container {
          name    = "wait-for-db"
          image   = "busybox:1.36"
          command = ["sh", "-c", "until nc -z postgres-service 5432; do echo waiting for db; sleep 2; done;"]
        }

        container {
          name  = "backend"
          image = "${aws_ecr_repository.backend.repository_url}:latest"

          port {
            container_port = 8000
          }

          env {
            name  = "DEBUG"
            value = "0"
          }

          env {
            name = "ALLOWED_HOSTS"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.lazysheeps_config.metadata[0].name
                key  = "ALLOWED_HOSTS"
              }
            }
          }

          env {
            name = "CORS_ALLOWED_ORIGINS"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.lazysheeps_config.metadata[0].name
                key  = "CORS_ALLOWED_ORIGINS"
              }
            }
          }

          env {
            name = "SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.lazysheeps_secret.metadata[0].name
                key  = "SECRET_KEY"
              }
            }
          }

          env {
            name  = "DATABASE_URL"
            value = "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgres-service:5432/$(POSTGRES_DB)"
          }

          env {
            name = "POSTGRES_USER"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.lazysheeps_config.metadata[0].name
                key  = "POSTGRES_USER"
              }
            }
          }

          env {
            name = "POSTGRES_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.lazysheeps_secret.metadata[0].name
                key  = "POSTGRES_PASSWORD"
              }
            }
          }

          env {
            name = "POSTGRES_DB"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.lazysheeps_config.metadata[0].name
                key  = "POSTGRES_DB"
              }
            }
          }

          liveness_probe {
            http_get {
              path = "/api/sync/health/"
              port = 8000
            }
            initial_delay_seconds = 60
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/api/sync/health/"
              port = 8000
            }
            initial_delay_seconds = 30
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 3
          }

          resources {
            requests = {
              memory = "512Mi"
              cpu    = "500m"
            }
            limits = {
              memory = "1Gi"
              cpu    = "1000m"
            }
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_service.postgres,
    aws_ecr_repository.backend
  ]
}

# Backend Service
resource "kubernetes_service" "backend" {
  metadata {
    name      = "backend-service"
    namespace = kubernetes_namespace.lazysheeps.metadata[0].name
  }

  spec {
    type = "ClusterIP"

    selector = {
      app = "backend"
    }

    port {
      port        = 8000
      target_port = 8000
      protocol    = "TCP"
    }
  }

  depends_on = [kubernetes_deployment.backend]
}

# Frontend Deployment
resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.lazysheeps.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "frontend"
      }
    }

    template {
      metadata {
        labels = {
          app = "frontend"
        }
      }

      spec {
        container {
          name  = "frontend"
          image = "${aws_ecr_repository.frontend.repository_url}:latest"

          port {
            container_port = 5173
          }

          env {
            name = "VITE_API_URL"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.lazysheeps_config.metadata[0].name
                key  = "VITE_API_URL"
              }
            }
          }

          env {
            name = "VITE_WS_URL"
            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.lazysheeps_config.metadata[0].name
                key  = "VITE_WS_URL"
              }
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 5173
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
          }

          readiness_probe {
            http_get {
              path = "/"
              port = 5173
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
          }

          resources {
            requests = {
              memory = "256Mi"
              cpu    = "250m"
            }
            limits = {
              memory = "512Mi"
              cpu    = "500m"
            }
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_service.backend,
    aws_ecr_repository.frontend
  ]
}

# Frontend Service
resource "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend-service"
    namespace = kubernetes_namespace.lazysheeps.metadata[0].name
  }

  spec {
    type = "LoadBalancer"

    selector = {
      app = "frontend"
    }

    port {
      port        = 80
      target_port = 5173
      protocol    = "TCP"
    }
  }

  depends_on = [kubernetes_deployment.frontend]
}
