# AMI RAG System - PTIT Intelligent Assistant 🎓

Hệ thống Chatbot thông minh sử dụng Retrieval-Augmented Generation (RAG) để cung cấp thông tin chính xác về Học viện Công nghệ Bưu chính Viễn thông (PTIT).

## 📋 Overview

**AMI** (Advanced Management Interface) là hệ thống RAG toàn diện với 2 use case chính:

### 1. Question Answering (QA) 💬
- Trả lời câu hỏi về PTIT sử dụng RAG
- 3 Thinking Modes:
  - **Fast** (gpt-4-1106-preview): Nhanh nhất, phù hợp câu hỏi đơn giản
  - **Balance** (gpt-4-0125-preview): Cân bằng tốc độ và chất lượng ⭐ *Default*
  - **Thinking** (o1-mini): Deep reasoning, chất lượng cao nhất
- Hỗ trợ streaming responses
- Tích hợp citations và sources

### 2. Document Management 📚
- Admin system với React UI
- JWT authentication
- CRUD operations:
  - ✅ Upload documents
  - ✅ Soft delete (không xóa vĩnh viễn)
  - ✅ Restore documents
  - ✅ Rename/update metadata
  - ✅ Collection management

## 🏗️ Architecture

### Tech Stack
```
┌──────────────────────────────────────────────────┐
│                   FRONTEND                       │
│        React + TypeScript + Material-UI          │
│              (Port: 6009)                        │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│                   BACKEND                        │
│           FastAPI + Python 3.12                  │
│              (Port: 6008)                        │
└──────────────────────────────────────────────────┘
                      ↓
┌─────────────────┬──────────────┬─────────────────┐
│     OpenAI      │  HuggingFace │     Qdrant      │
│  (LLM Models)   │  (Embeddings)│ (Vector Store)  │
└─────────────────┴──────────────┴─────────────────┘
                      ↓
┌─────────────────┬──────────────┐
│    MongoDB      │    Redis     │
│  (Users, Docs)  │   (Cache)    │
└─────────────────┴──────────────┘
```

### Components

| Component | Purpose | Port |
|-----------|---------|------|
| **FastAPI** | Backend API | 6008 |
| **React UI** | Admin Interface | 6009 |
| **MongoDB** | Users & Documents Metadata | 27017 |
| **Qdrant** | Vector Database | 6333 |
| **Redis** | Caching Layer | 6379 |

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Node.js 18+ (for frontend)

### 1. Clone & Setup
```bash
git clone <repository>
cd Ami

# Copy environment file
cp env.example.txt .env
# Edit .env and fill in your OpenAI API key and other configs
```

### 2. Start Services
```bash
# Start all services (MongoDB, Qdrant, Redis)
make up

# Check services health
make health
```

### 3. Initialize Backend
```bash
# Install Python dependencies
uv sync

# Create first admin user
make create-admin

# Migrate existing documents
make migrate
```

### 4. Start Backend
```bash
# Development
make dev

# Or with uvicorn directly
uvicorn app.api.main:app --host 0.0.0.0 --port 6008 --reload
```

### 5. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📖 Usage

### Admin Panel
1. Open http://localhost:6009
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin`
   - ⚠️ **Change password after first login!**
3. Manage documents via UI

### API Documentation
- Swagger UI: http://localhost:6008/docs
- ReDoc: http://localhost:6008/redoc

### Example API Calls

#### 1. Login
```bash
curl -X POST http://localhost:6008/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

#### 2. Ask Question (Fast Mode)
```bash
curl -X POST http://localhost:6008/api/v1/generate/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "messages": [{"role": "user", "content": "PTIT có những ngành nào?"}],
    "thinking_mode": "fast",
    "rag_config": {"enabled": true, "top_k": 5}
  }'
```

#### 3. Upload Document (Admin only)
```bash
curl -X POST http://localhost:6008/api/v1/admin/documents/?collection=ptit_docs \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf"
```

## 🛠️ Development

### Project Structure
```
Ami/
├── app/
│   ├── api/                    # FastAPI routes
│   │   ├── main.py            # App entry point
│   │   ├── routes.py          # Q&A endpoints
│   │   ├── auth_routes.py     # Authentication
│   │   └── admin_routes.py    # Document management
│   ├── application/           # Business logic
│   │   ├── factory.py         # Provider factory (singleton)
│   │   └── services.py        # RAG & Document services
│   ├── core/                  # Domain models
│   │   ├── interfaces.py      # Abstract interfaces
│   │   ├── models.py          # Pydantic models
│   │   ├── mongodb_models.py  # MongoDB schemas
│   │   └── auth.py            # JWT utilities
│   ├── infrastructure/        # External integrations
│   │   ├── databases/         # DB clients
│   │   ├── embeddings/        # Embedding providers
│   │   ├── llms/              # LLM providers
│   │   ├── vector_stores/     # Vector stores
│   │   └── tools/             # Utilities
│   └── config/
│       └── settings.py        # Configuration
├── frontend/                  # React Admin UI
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── pages/            # Pages (Login, Dashboard, Documents)
│   │   └── store/            # State management
│   └── package.json
├── scripts/
│   ├── create_admin_user.py          # Bootstrap admin
│   └── migrate_data_to_mongodb.py    # Data migration
├── assets/raw/               # Source documents
├── docker-compose.yml        # Services orchestration
├── Makefile                  # Convenience commands
└── pyproject.toml           # Python dependencies
```

### Key Design Principles
- ✅ **Clean Architecture**: Clear separation of concerns
- ✅ **SOLID Principles**: Maintainable and extensible
- ✅ **Dependency Injection**: Factory pattern for providers
- ✅ **Async/Await**: Non-blocking I/O
- ✅ **Type Safety**: Pydantic models + TypeScript

### Makefile Commands
```bash
make up              # Start all services
make down            # Stop all services
make dev             # Run backend in dev mode
make create-admin    # Create first admin user
make migrate         # Import documents from assets/raw/
make health          # Check system health
make clean           # Clean up containers and volumes
make logs            # View service logs
```

## 🔧 Configuration

### Thinking Modes Mapping
| Mode | OpenAI Model | Use Case |
|------|--------------|----------|
| `fast` | gpt-4-1106-preview | Quick responses, simple Q&A |
| `balance` | gpt-4-0125-preview | General purpose (default) |
| `thinking` | o1-mini | Complex reasoning, detailed analysis |

### Environment Variables
See `env.example.txt` for all available options.

Key variables:
- `OPENAI_API_KEY`: Required for LLM
- `JWT_SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `APP_PORT`: Default 6008
- `MONGODB_HOST`, `QDRANT_HOST`, `REDIS_HOST`: Service endpoints

## 🧪 Testing

### Health Check
```bash
# Check all services
curl http://localhost:6008/api/v1/config/health

# Expected response:
# {
#   "status": "healthy",
#   "databases": {
#     "mongodb": "ok",
#     "redis": "ok",
#     "qdrant": "ok"
#   }
# }
```

### Test Document Upload
```bash
# Upload a test document
cd assets/raw
make test-upload FILE=ChuongTrinhAnToanThongTinChatLuongCao.md
```

## 📊 Monitoring

- **API Metrics**: Available at `/api/v1/config/health`
- **Database Stats**: `/api/v1/vectordb/stats`
- **Provider Status**: `/api/v1/config/providers`

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- API key protection
- Soft delete (no data loss)

## 🐛 Troubleshooting

### Services not starting
```bash
# Check Docker
docker ps

# View logs
make logs

# Restart services
make down && make up
```

### MongoDB connection error
```bash
# Verify MongoDB is running
docker exec -it ami_mongodb mongosh --eval "db.adminCommand('ping')"
```

### Qdrant connection error
```bash
# Check Qdrant health
curl http://localhost:6333/healthz
```

### Frontend can't connect to backend
- Ensure backend is running on port 6008
- Check CORS settings in `.env`
- Verify API proxy in `frontend/vite.config.ts`

## 📝 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/register` - Register user (Admin only)

### Q&A Endpoints
- `POST /api/v1/generate/chat` - Generate response with RAG
- `POST /api/v1/generate/stream` - Streaming response

### Admin Document Endpoints (Auth Required)
- `GET /api/v1/admin/documents/` - List documents
- `POST /api/v1/admin/documents/` - Upload document
- `GET /api/v1/admin/documents/{id}` - Get document
- `PUT /api/v1/admin/documents/{id}` - Update document
- `DELETE /api/v1/admin/documents/{id}` - Soft delete
- `POST /api/v1/admin/documents/{id}/restore` - Restore document

### Vector DB Endpoints
- `POST /api/v1/vectordb/upload` - Upload to vector store
- `POST /api/v1/vectordb/search` - Semantic search
- `GET /api/v1/vectordb/stats` - Database statistics

## 🤝 Contributing

This project follows Clean Architecture and SOLID principles. Please maintain:
- Type hints
- Async/await patterns
- Pydantic models for validation
- Comprehensive docstrings

## 📄 License

Private - For PTIT internal use only

## 🙏 Credits

Built with:
- FastAPI
- React + Material-UI
- OpenAI GPT-4 & O1
- Qdrant Vector Database
- MongoDB
- HuggingFace Transformers

---

**Made with ❤️ for PTIT**
