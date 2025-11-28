# Clean Architecture Refactoring Guide

## ✅ Đã hoàn thành (4 commits)

### Phase 1: Domain Layer (100%)
- 26 files: Enums, Entities, Value Objects, Exceptions
- Pure Python, 0 framework dependencies
- Business logic in entities

### Phase 2: Application Layer (90%)  
- 14 interface files (Repositories + Services)
- 15 use case files (Auth, Chat, Documents, RAG)
- Clean separation of concerns

### Phase 3: Infrastructure Layer (Partial - 40%)
- MongoDB mappers (Entity ↔ Model)
- 2 Repository implementations (User, Chat)
- Auth infrastructure (JWT, Password hasher)

### Example: Refactored Auth Routes
- See `app/presentation/api/routes/auth_routes_example.py`
- Demonstrates use of use cases in routes
- Shows benefits vs old approach

## 📊 Statistics

- **Files created**: 65+ files
- **Lines of code**: ~6,000+ lines
- **Git commits**: 4 commits
- **Progress**: ~40% of full refactoring

## 🎯 How to Use New Architecture

### 1. Domain Layer (Pure Business Logic)

```python
# Domain Entity with business logic
from app.domain.entities.user import User

user = User(id="1", username="test", email="test@example.com", ...)
user.add_role("admin")
user.record_login()
assert user.has_admin_privileges() == True
```

### 2. Application Layer (Use Cases)

```python
# Use case orchestrates workflow
from app.application.use_cases.auth import LoginUserUseCase, LoginUserInput

use_case = LoginUserUseCase(user_repository, password_hasher)
result = await use_case.execute(
    LoginUserInput(username="admin", password="secret")
)
# Returns domain entity
user = result.user
```

### 3. Infrastructure Layer (Implementations)

```python
# Repository implements interface
from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository

db = await get_database()
user_repo = MongoDBUserRepository(db)

# Works with domain entities
user = await user_repo.get_by_username("admin")
```

### 4. Presentation Layer (Routes)

```python
# Route is thin, delegates to use case
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUserUseCase = Depends(get_login_use_case),
):
    result = await use_case.execute(...)
    return LoginResponse(...)
```

## 🔄 Migration Strategy

### Step 1: Keep Old Code Working
- Old routes in `app/api/` still work
- New architecture in `app/domain/`, `app/application/`, etc.
- Gradual migration

### Step 2: Refactor Routes One by One
1. Pick a route (e.g., `/auth/login`)
2. Create use case if not exists
3. Update route to use use case
4. Test thoroughly
5. Move to next route

### Step 3: Remove Old Code
- After all routes migrated
- Delete old `app/core/` (models, interfaces)
- Clean up unused imports

## 🧪 Testing New Architecture

### Unit Tests (Domain)
```python
def test_user_entity():
    user = User(id="1", username="test", ...)
    user.add_role("admin")
    assert user.has_admin_privileges()
```

### Integration Tests (Use Cases)
```python
async def test_login_use_case():
    # Mock repository
    mock_repo = Mock(IUserRepository)
    mock_repo.get_by_username.return_value = test_user
    
    use_case = LoginUserUseCase(mock_repo, password_hasher)
    result = await use_case.execute(LoginUserInput(...))
    
    assert result.user.username == "test"
```

### E2E Tests (Routes)
```python
async def test_login_endpoint(client):
    response = await client.post("/auth/login", data={
        "username": "test",
        "password": "secret",
    })
    assert response.status_code == 200
```

## 📁 Directory Structure

```
app/
├── domain/              # Pure business logic
│   ├── entities/        # Business entities
│   ├── value_objects/   # Immutable values
│   ├── enums/           # Domain enums
│   └── exceptions/      # Domain errors
│
├── application/         # Application logic
│   ├── use_cases/       # Business workflows
│   │   ├── auth/
│   │   ├── chat/
│   │   ├── documents/
│   │   └── rag/
│   ├── interfaces/      # Ports (contracts)
│   │   ├── repositories/
│   │   └── services/
│   └── services/        # Application services
│
├── infrastructure/      # External concerns
│   ├── db/
│   │   └── mongodb/     # MongoDB client & mappers
│   ├── repositories/    # Repository implementations
│   ├── auth/            # JWT, Password hashing
│   ├── llms/            # LLM providers
│   ├── embeddings/      # Embedding providers
│   └── vector_stores/   # Qdrant, etc.
│
├── presentation/        # API layer
│   └── api/
│       ├── routes/      # Refactored routes
│       └── schemas/     # DTOs
│
└── config/              # Configuration
```

## 🚀 Next Steps

### TODO: Complete Refactoring

1. **Finish Infrastructure Layer**:
   - [ ] DocumentRepository implementation
   - [ ] FileRepository implementation
   - [ ] CrawlerRepository implementation
   - [ ] Copy existing LLM/Embedding implementations
   - [ ] Update imports in existing implementations

2. **Refactor All Routes**:
   - [ ] auth_routes.py ✅ (example exists)
   - [ ] chat_history_routes.py
   - [ ] generate_routes.py (RAG)
   - [ ] image_routes.py
   - [ ] vectordb_routes.py
   - [ ] admin_routes.py
   - [ ] crawler_routes.py

3. **Create DTOs**:
   - [ ] auth_dto.py
   - [ ] chat_dto.py
   - [ ] document_dto.py
   - [ ] rag_dto.py

4. **Testing**:
   - [ ] Unit tests for domain entities
   - [ ] Unit tests for use cases
   - [ ] Integration tests for repositories
   - [ ] E2E tests for routes

5. **Cleanup**:
   - [ ] Remove old `app/core/` files
   - [ ] Update all imports
   - [ ] Update documentation

## 💡 Best Practices

1. **Keep Domain Pure**: No framework dependencies in `domain/`
2. **Single Responsibility**: One use case = one workflow
3. **Dependency Inversion**: Depend on interfaces, not implementations
4. **Test Each Layer**: Domain → Application → Infrastructure → Presentation
5. **Fail Fast**: Validate early (value objects, use case inputs)

## 📚 Learn More

- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- DDD: Domain-Driven Design by Eric Evans
