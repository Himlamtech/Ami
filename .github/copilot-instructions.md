# AMI Project - Coding Guidelines

> AMI Intelligent Assistant - RAG-Powered Chatbot System

---

## ⚡ QUICK START WORKFLOW

**Mỗi lần code, làm theo thứ tự này:**

1. **📖 Đọc docs usecase** → Hiểu luồng chính
   - Vào `/docs/usecase/` chọn file liên quan (01_CHAT, 02_INGESTION, 04_ADMIN, etc)
   - Đọc flow diagram + data model + API schema
   - Hiểu error handling, edge cases

2. **🏗️ Check architecture** → Biết code vào đâu
   - Backend: `backend/app/{config,domain,application,infrastructure,api}`
   - Frontend: `frontend/src/{pages,components,api,hooks}`
   - Xem file tương tự đã có để theo pattern

3. **💻 Code ngắn gọn** → Không over-engineer
   - YAGNI: Chỉ code cần thiết
   - KISS: Đơn giản > Phức tạp
   - Verify: Test luồng trước khi commit

---

## 📚 Use Cases Reference (Pick One Before Coding)

| Cần code | Xem file này | Flow |
|---------|------------|------|
| Chat, Q&A, Voice, Image | **01_CHAT_WORKFLOWS.md** | User query → Embed → Search → Generate |
| Upload, Crawler, Approval, Processing | **02_INGESTION_WORKFLOWS.md** | File/URL → Parse → Chunk (300-500) → Embed → Store |
| Bookmarks, Suggestions, Engagement | **03_USER_ENGAGEMENT.md** | User action → Analyze → Recommend |
| Analytics, Feedback, Cost, Dashboard | **04_ADMIN_ANALYTICS.md** | Collect → Aggregate → Display |
| User management, Ban, Profile, Settings | **05_ADMIN_USER_MANAGEMENT.md** | Search → Filter → Action |
| Index & Overview | **00_INDEX.md** | Tra cứu nhanh all 19 UCs |

---

## 🏗️ Code Organization

### Backend (Python)
```
backend/app/
├── domain/          # Entities, business logic (NO external deps)
├── application/     # Use cases, interfaces (depends on domain)
├── infrastructure/  # DB, AI, external services
└── api/            # Routes, schemas, middleware
```

### Frontend (TypeScript/React)
```
frontend/src/
├── pages/          # Full page components
│   ├── user/       # Chat, Bookmarks, Profile
│   └── admin/      # Analytics, Users, Feedback, Conversations
├── components/     # Reusable UI components
├── api/            # API clients (user-api.ts, admin-api.ts)
├── hooks/          # Custom React hooks
└── utils/          # Helper functions
```

### Routes
- User: `/api/v1/chat`, `/api/v1/bookmarks`, `/api/v1/users/profile`
- Admin: `/api/v1/admin/analytics`, `/api/v1/admin/users`, `/api/v1/admin/documents`

---

## ✅ Checklist Trước Khi Commit

- [ ] Đã đọc docs usecase liên quan?
- [ ] Code follow pattern tương tự file khác?
- [ ] Không hardcode config/secrets (dùng .env)?
- [ ] Imports đúng layer (domain → application → infrastructure)?
- [ ] Test đạt (nếu có)?
- [ ] < 200 lines/file (nếu > thì split)?
- [ ] Không over-engineer?

---

## 📋 Coding Philosophy

- **Simple first**: Giải quyết bằng cách đơn giản nhất trước
- **Readable**: Code phải hiểu được sau 6 tháng
- **Configurable**: Model, endpoints, timeouts → env var, không hardcode
- **No over-engineering**: Không tạo abstraction khi chưa cần
- **YAGNI**: Chỉ code feature thực sự cần

---

## 🔗 Key Files

- **Docs**: `docs/usecase/*.md` (đọc trước khi code!)
- **Backend Main**: `backend/main.py`
- **Frontend Main**: `frontend/src/App.tsx`
- **Config**: `backend/app/config/*.py`
- **Middleware**: `backend/app/api/middleware/`

---

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

## 4. Code Organization by Layer

| Layer | Path | Purpose |
|-------|------|---------|
| Domain | `domain/entities/` | Business logic, NO external deps |
| Application | `application/use_cases/` | Workflows, interfaces |
| Infrastructure | `infrastructure/<type>/` | DB, AI, external APIs |
| API | `api/v1/<feature>/` | Routes, schemas |

## 5. Naming Conventions

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

---

## 📌 Before You Code

**ALWAYS check these first:**

1. Is there a similar file in the codebase?
   - Follow the same pattern
   
2. Does the feature have a usecase doc?
   - Read `docs/usecase/*.md`
   - Understand the flow

3. Is this in the right layer?
   - Domain logic → `domain/`
   - Use case → `application/use_cases/`
   - Data access → `infrastructure/`
   - Route handler → `api/`

---

**Remember: Docs → Code → Test ✅**
