# Docker Setup Guide for LazySheeps

This guide explains how to run the LazySheeps application using Docker.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+

## Quick Start

### 1. Clone the repository (if not already done)
```bash
git clone https://github.com/riyamittal12426/LazySheeps.git
cd LazySheeps
```

### 2. Create environment file
```bash
cp .env.example .env
```

Edit `.env` and update the values as needed (especially the SECRET_KEY in production).

### 3. Build and start all services
```bash
docker-compose up --build
```

Or run in detached mode (background):
```bash
docker-compose up -d --build
```

### 4. Access the application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Backend Admin**: http://localhost:8000/admin
- **Database**: localhost:5432

## Docker Commands

### Start services
```bash
docker-compose up
```

### Start in background
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes database data)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Restart a service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Execute commands in containers

#### Backend (Django commands)
```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Open Python shell
docker-compose exec backend python manage.py shell

# Run tests
docker-compose exec backend python manage.py test
```

#### Frontend (npm commands)
```bash
# Install new package
docker-compose exec frontend npm install <package-name>

# Run build
docker-compose exec frontend npm run build
```

#### Database
```bash
# Access PostgreSQL
docker-compose exec db psql -U lazysheeps_user -d lazysheeps_db

# Backup database
docker-compose exec db pg_dump -U lazysheeps_user lazysheeps_db > backup.sql

# Restore database
docker-compose exec -T db psql -U lazysheeps_user lazysheeps_db < backup.sql
```

## Rebuild after changes

### Rebuild all containers
```bash
docker-compose up --build
```

### Rebuild specific service
```bash
docker-compose up --build backend
docker-compose up --build frontend
```

### Force rebuild (no cache)
```bash
docker-compose build --no-cache
docker-compose up
```

## Troubleshooting

### Port already in use
If you get port conflicts, change the ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8001 to your preferred port
```

### Database connection issues
```bash
# Check if database is healthy
docker-compose ps

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Frontend not updating
```bash
# Clear node_modules volume
docker-compose down
docker volume rm lazysheeps_node_modules
docker-compose up --build
```

### Backend migrations not running
```bash
# Manually run migrations
docker-compose exec backend python manage.py migrate

# Check migration status
docker-compose exec backend python manage.py showmigrations
```

## Production Deployment

For production, make these changes:

1. Update `.env`:
   - Set `DEBUG=0`
   - Use a strong `SECRET_KEY`
   - Add your domain to `ALLOWED_HOSTS`
   - Update `CORS_ALLOWED_ORIGINS` with your frontend domain

2. Use production-ready images:
   - Add Nginx reverse proxy
   - Use Gunicorn for Django instead of runserver
   - Build optimized frontend

3. Add SSL/TLS certificates

4. Use managed database service (AWS RDS, etc.)

5. Set up proper logging and monitoring

## Docker Compose Services

### Backend (Django)
- **Port**: 8000
- **Volume**: `./backend:/app` (for development hot-reload)
- **Depends on**: Database

### Frontend (React/Vite)
- **Port**: 5173
- **Volume**: `./frontend:/app` (for development hot-reload)
- **Depends on**: Backend

### Database (PostgreSQL)
- **Port**: 5432
- **Volume**: `postgres_data` (persistent storage)
- **Health check**: Ensures database is ready before starting backend

## Notes

- The setup includes hot-reload for both frontend and backend in development
- Database data persists in Docker volumes even when containers are stopped
- To reset everything: `docker-compose down -v && docker-compose up --build`
