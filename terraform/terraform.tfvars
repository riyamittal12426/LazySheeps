# AWS Configuration
aws_region = "us-east-1"

# EKS Cluster Configuration
cluster_name    = "lazysheeps-cluster"
cluster_version = "1.28"
environment     = "production"

# Node Configuration
node_instance_type = "t3.medium"
node_desired_size  = 2
node_min_size      = 2
node_max_size      = 4

# VPC Configuration
vpc_cidr = "10.0.0.0/16"

# Application Secrets (CHANGE THESE!)
postgres_password    = "changeme-secure-password-123"
django_secret_key    = "changeme-django-secret-key-here-make-it-long-and-random"
github_client_id     = ""
github_client_secret = ""
