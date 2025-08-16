# 🐳 AmiAgent Docker - Clean & Optimized

## 📁 Simplified Structure
```
├── Dockerfile              # Multi-stage build (production + development)
├── docker-compose.yml      # All-in-one orchestration with profiles
├── .dockerignore           # Build optimization
├── Makefile               # Docker commands shortcuts
└── DOCKER.md              # This documentation
```

## 🚀 Quick Start Commands

### Production (Optimized Build)
```bash
make docker-up
# OR: docker compose up --build -d
```

### Development (Hot Reload + Tools)
```bash
make docker-dev  
# OR: APP_ENV=dev DOCKER_TARGET=development docker compose --profile tools up --build -d
```

### Tools Only (pgAdmin + Redis Commander)
```bash
make docker-tools
# OR: docker compose --profile tools up --build -d
```

## 🎯 Multi-Stage Build Benefits

### Production Stage (`final`)
- ✅ Minimal dependencies (no dev tools)
- ✅ Smaller image size (~200MB vs ~500MB)
- ✅ Security optimized (no build tools)
- ✅ Fast startup time

### Development Stage (`development`)  
- ✅ All dev dependencies included
- ✅ Hot reload enabled
- ✅ Git and build tools available
- ✅ Source code mounted as volume

## 📊 Access URLs
- **🌐 API**: http://localhost:1912
- **🗄️ pgAdmin**: http://localhost:5050 (admin@amiagent.com / admin123)
- **🔴 Redis Commander**: http://localhost:8081

## 🔧 Essential Commands
```bash
# View application logs
make docker-logs

# Check service health
make docker-status

# Stop everything
make docker-down

# Clean rebuild
make docker-restart

# Complete cleanup (DESTRUCTIVE!)
make docker-clean
```

## ⚡ Performance Optimizations

1. **Multi-stage builds** - Separate prod/dev stages
2. **Layer caching** - Dependencies cached separately  
3. **BuildKit** - Parallel builds and cache mounting
4. **tmpfs mounts** - Cache directories in memory
5. **Minimal base** - python:3.12-slim for smaller images
6. **Health checks** - Proper startup detection

## 🛠️ Advanced Usage

### Environment Variables
```bash
# Development with custom settings
APP_ENV=dev DEBUG=true docker compose up -d

# Production with specific target
DOCKER_TARGET=final docker compose up --build -d
```

### Development Workflow
```bash
# 1. Start development environment
make docker-dev

# 2. Make code changes (auto-reloads)
# Files are mounted as volume for instant feedback

# 3. Test API
make docker-test-api

# 4. Run tests in container  
make docker-test
```

## 📋 Setup Requirements
1. **Environment**: Create `.env` file with API keys
2. **Database**: `init-db.sql` for PostgreSQL setup
3. **Directories**: `storage/` and `logs/` (auto-created)
4. **Docker**: Docker + Docker Compose installed
