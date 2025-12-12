# AMI Project - Copilot Instructions

> PTIT Intelligent Assistant - RAG-Powered Chatbot System

---

## 1. Coding Philosophy

### Mindset
- **Simple first**: Giải quyết vấn đề bằng cách đơn giản nhất trước
- **No over-engineering**: Không tạo abstraction khi chưa cần
- **Pragmatic**: Code hoạt động > Code "đẹp" nhưng phức tạp
- **Readable**: Code phải dễ đọc, dễ hiểu sau 6 tháng
- **Configurable**: Mọi thứ trong code có thể thay đổi đều phải qua config/env, ví dụ như model, endpoints, timeouts, thresholds đều phải set thông qua config mà không được hardcode
- **Environment**: Chạy venv trước khi run/test/codegen để active dependencies đúng đã cài đặt
### Code Style
```python
# ✅ Good - Ngắn gọn, rõ ràng
class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo
    
    async def get_user(self, id: str) -> User | None:
        return await self.repo.find_by_id(id)

# ❌ Bad - Over-engineering
class UserService:
    def __init__(self, repo: IUserRepository, cache: ICache, logger: ILogger, ...):
        self._repo = repo
        self._cache = cache
        self._logger = logger
        # 10 more dependencies...
    
    async def get_user(self, id: str) -> Result[User, Error]:
        # 50 lines of "defensive" code
```

### Principles
1. **YAGNI**: Không code feature chưa cần
2. **KISS**: Keep It Simple, Stupid
3. **DRY**: Nhưng đừng quá sớm - duplicate 2 lần OK, 3 lần thì refactor
4. **Single file > Multiple files**: Nếu < 200 lines, giữ trong 1 file

### When Using AI/MCP Tools
- Đọc context đầy đủ trước khi sửa
- Sửa từng phần nhỏ, test ngay
- Không generate code dài > 100 lines/lần
- Prefer edit existing > create new

---

## 2. Project Requirements

### Package Management
```bash
# Dùng uv - KHÔNG dùng pip
uv sync              # Install dependencies
uv add <package>     # Add new package
uv run python ...    # Run with venv
```

### Configuration Rules
```python
# ✅ Correct - Dùng config từ app/config/
from app.config import mongodb_config, openai_config

class MyService:
    def __init__(self, config: MongoDBConfig = None):
        self.config = config or mongodb_config

# ❌ Wrong - Hardcode hoặc tự tạo config
class MyService:
    def __init__(self, host="localhost", port=27017):  # KHÔNG ĐƯỢC!
        ...
```

### Environment Variables
- Tất cả secrets/config → file `.env`
- pydantic-settings tự map: `field_name` → `FIELD_NAME`
- Không dùng `os.getenv()` trực tiếp trong code

### Code Organization
| Cần làm | Vị trí |
|---------|--------|
| Business logic | `domain/entities/` |
| Use case | `application/use_cases/<feature>/` |
| Interface | `application/interfaces/` |
| Implementation | `infrastructure/<category>/` |
| API endpoint | `api/routes/` |
| Config | `config/<category>.py` |

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Repository: `mongodb_<entity>_repository.py`
- Route: `<domain>_routes.py`

---

## 3. Use Cases

### USER Features (Student-facing)
| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| UC-U-001 | Smart Q&A | RAG với personalization theo profile | ✅ Done |
| UC-U-002 | Voice Query | STT (Wav2Vec2/Gemini) → RAG → Response | ✅ Done |
| UC-U-003 | Image Query | Vision AI → RAG → Response | ✅ Done |
| UC-U-004 | Bookmark Q&A | Lưu Q&A quan trọng với tags, notes | 🔄 Planned |
| UC-U-005 | Session Management | CRUD conversations, search, export | ✅ Done |
| UC-U-006 | Feedback | 👍👎, rating 1-5, categories | ✅ Done |
| UC-U-007 | Suggestions | Related questions, popular topics | 🔄 Planned |
| UC-U-008 | Profile Settings | Major, level, preferences | ✅ Done |

### ADMIN Features
| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| UC-A-001 | Conversation History | View/filter/export all sessions | 🔄 Planned |
| UC-A-002 | Feedback Dashboard | Analytics, trends, negative feedback | 🔄 Planned |
| UC-A-003 | Usage Analytics | Requests, DAU/MAU, latency, errors | 🔄 Planned |
| UC-A-004 | Cost Tracking | LLM token usage, cost by provider/model | 🔄 Planned |
| UC-A-005 | Knowledge Quality | Coverage, gaps, low-confidence queries | 🔄 Planned |
| UC-A-006 | User Profiles | View profiles, interests, engagement | 🔄 Planned |
| UC-A-007 | Document Management | Upload, version, approve, delete | ✅ Done |
| UC-A-008 | Data Sources | Crawl config, schedule, sync | ✅ Done |

### Data Pipeline (Existing)
- **Ingest**: Upload files, web scraping, web crawling
- **Approval**: Pending updates workflow với diff viewer
- **Sync**: Scheduled crawling, change detection
- **Vector**: Auto-chunking, embedding, indexing

---

## 4. Architecture

### Clean Architecture (4 Layers)
```
app/
├── domain/           # Core entities - NO external deps
├── application/      # Use cases & interfaces
├── infrastructure/   # External implementations
└── api/              # FastAPI routes & DTOs
```

**Rule**: Dependencies point INWARD only.
- `domain` → knows nothing
- `application` → knows `domain`
- `infrastructure` → knows `application`, `domain`
- `api` → knows all

### Folder Structure
```
app/
├── config/                    # All configurations
│   ├── base.py               # AppConfig
│   ├── persistence.py        # MongoDB, Qdrant, MinIO
│   ├── ai.py                 # OpenAI, Anthropic, Embeddings
│   └── external.py           # Firecrawl, etc.
│
├── domain/
│   ├── entities/             # Business objects
│   ├── enums/                # Enumerations
│   ├── exceptions/           # Domain exceptions
│   └── value_objects/        # Immutable value types
│
├── application/
│   ├── interfaces/           # Abstract interfaces
│   │   ├── repositories/     # Data access contracts
│   │   ├── services/         # Service contracts
│   │   └── processors/       # Processing contracts
│   ├── use_cases/            # Business operations
│   │   ├── chat/
│   │   ├── rag/
│   │   ├── documents/
│   │   └── ...
│   └── services/             # Application services
│
├── infrastructure/
│   ├── persistence/          # Data storage
│   │   ├── mongodb/          # Document DB
│   │   ├── qdrant/           # Vector DB
│   │   └── minio/            # File storage
│   ├── ai/                   # AI services
│   │   ├── llm/              # LLM providers
│   │   ├── embeddings/       # Text embeddings
│   │   └── stt/              # Speech-to-Text
│   ├── external/             # Third-party APIs
│   ├── processing/           # Data transformation
│   ├── scheduling/           # Background jobs
│   └── factory/              # DI container
│
└── api/
    ├── routes/               # API endpoints
    ├── schemas/              # Request/Response DTOs
    ├── dependencies/         # FastAPI dependencies
    └── middleware/           # Custom middleware
```

### Key Patterns

**1. Factory Pattern (DI)**
```python
factory = get_factory()
llm = factory.get_llm_service(provider="openai")
```

**2. Repository Pattern**
```python
class IUserRepository(ABC):
    async def find_by_id(self, id: str) -> User | None: ...

class MongoDBUserRepository(IUserRepository):
    async def find_by_id(self, id: str) -> User | None:
        # MongoDB implementation
```

**3. Use Case Pattern**
```python
class QueryWithRAGUseCase:
    def __init__(self, embedding_svc, vector_store, llm_svc):
        # Inject interfaces, not implementations
    
    async def execute(self, input: QueryInput) -> QueryOutput:
        # 1. Embed → 2. Search → 3. Generate
```

### External Services

| Service  | Port  | Purpose                        |
|----------|-------|--------------------------------|
| MongoDB  | 27017 | Documents, users, chat history |
| Qdrant   | 6333  | Vector embeddings              |
| MinIO    | 9000  | File storage (S3-compatible)   |
| Backend  | 11121 | FastAPI API                    |
| Frontend | 11120 | React dev server               |

### Quick Commands
```bash
make up              # Start Docker services
make dev             # Run backend
make frontend        # Run frontend
make migrate         # Import documents
```

---

## 5. New Entities (Planned)

### Analytics & Tracking
```python
UsageMetric      # Request/latency/error tracking
LLMUsage         # Token usage, cost per provider/model
SearchLog        # Query logs for gap detection
```

### User Experience
```python
Bookmark         # Saved Q&A pairs with tags
Suggestion       # Proactive recommendations
PromptTemplate   # Dynamic system prompts
```

### Configuration
```python
ModelConfig      # LLM model settings per use case
DocumentVersion  # Document versioning
```

---

## 6. API Endpoints (Planned)

### Admin Analytics
```
GET  /api/v1/admin/analytics/overview
GET  /api/v1/admin/analytics/costs
GET  /api/v1/admin/analytics/usage
GET  /api/v1/admin/feedback/dashboard
GET  /api/v1/admin/knowledge/gaps
GET  /api/v1/admin/conversations
```

### User Features
```
POST /api/v1/bookmarks
GET  /api/v1/bookmarks
GET  /api/v1/suggestions
POST /api/v1/chat/sessions/{id}/export
```
