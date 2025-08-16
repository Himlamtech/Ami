# 🐳 Docker Quick Start

## Files Structure (Simplified)
```
├── Dockerfile              # App container definition
├── docker-compose.yml      # All-in-one orchestration  
└── .dockerignore           # Build optimization
```

## Usage Commands

### 🚀 Production
```bash
docker compose up -d
```

### 🔥 Development (Hot Reload)
```bash
APP_ENV=dev docker compose up -d
```

### 🛠️ Development + Tools (pgAdmin + Redis Commander)
```bash
APP_ENV=dev docker compose --profile tools up -d
```

### 📊 Access URLs
- **API**: http://localhost:1912
- **pgAdmin**: http://localhost:5050 (admin@amiagent.com / admin123)
- **Redis Commander**: http://localhost:8081

### 🔧 Useful Commands
```bash
# View logs
docker compose logs -f amiagent

# Stop everything
docker compose down

# Rebuild and restart
docker compose up --build -d

# Clean up (remove volumes)
docker compose down -v
```

### 📁 Setup Requirements
1. Create `.env` file with your API keys
2. Ensure `init-db.sql` exists for database setup
3. Create `storage/` and `logs/` directories (auto-created)
