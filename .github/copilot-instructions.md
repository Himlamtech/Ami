# AMI Project - Copilot Instructions

> PTIT Intelligent Assistant - RAG-Powered Chatbot System

---

## 1. Coding Philosophy

### Mindset
- **Simple first**: Giải quyết vấn đề bằng cách đơn giản nhất trước
- **No over-engineering**: Không tạo abstraction khi chưa cần
- **Pragmatic**: Code hoạt động > Code "đẹp" nhưng phức tạp
- **Readable**: Code phải dễ đọc, dễ hiểu sau 6 tháng

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

### Chat & Q&A
- Text chat với RAG (retrieve from knowledge base)
- Multi-turn conversation với context awareness
- Voice input (Speech-to-Text với Wav2Vec2)
- File upload (PDF, DOCX, TXT, MD, CSV)
- Streaming responses

### Data Management
- **Ingest**: Upload files, web scraping, web crawling
- **View**: Statistics, collections, document metadata
- **Delete**: Soft delete với restore capability
- **Re-index**: Update vector embeddings

### Admin Operations
- User management (CRUD)
- Data source approval workflow
- Sync data between sources
- System configuration

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
