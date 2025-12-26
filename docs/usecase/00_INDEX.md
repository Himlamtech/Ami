# AMI USE CASE DOCUMENTATION - COMPLETE GUIDE

## Overview

This directory contains comprehensive use case documentation for the AMI (PTIT Intelligent Assistant) system. Each use case includes:
- Complete workflow diagrams (Mermaid)
- Sequence diagrams with all interactions
- Data models (JSON schemas)
- API endpoints
- Error handling & recovery strategies
- Performance metrics & SLA targets
- Integration points

---

## Available Use Cases (Completed)

### User Features (Student-Facing)

#### UC-001: Intelligent Chat Interaction with RAG
**File:** [chat.md](chat.md) - Sections 1-3

Core functionality for text-based Q&A with Retrieval-Augmented Generation.

**Workflow:**
- User submits question → Validation → Session management → Query embedding
- Hybrid search (Semantic + BM25) → Document retrieval → LLM generation
- Response streaming → Message persistence → Analytics

**Coverage:**
- Session lifecycle & data model
- Complete query processing flow (36 steps)
- Authentication & authorization
- Context window management
- Caching & optimization

**Key Endpoints:**
```
POST   /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{id}
POST   /api/v1/chat/send-message
GET    /api/v1/chat/sessions/{id}/export
```

---

#### UC-002: Voice Query Processing
**File:** [chat.md](chat.md) - Section 4

Enable hands-free interaction via speech-to-text.

**Workflow:**
- Audio capture → STT (Wav2Vec2 or Gemini) → Confidence validation
- Text query → RAG pipeline → LLM generation → Optional TTS
- Response streaming with audio

**Coverage:**
- Audio validation & format support
- STT provider fallback strategy
- Confidence scoring & user verification
- TTS conversion (optional)
- Error handling for audio issues

**Key Endpoints:**
```
POST   /api/v1/chat/voice-query
POST   /api/v1/chat/voice-stream (WebSocket)
```

---

#### UC-003: Image Query Processing
**File:** [chat.md](chat.md) - Section 5

Process images (announcements, schedules, etc.) with Vision AI + OCR.

**Workflow:**
- Image upload & validation → Vision AI analysis → OCR text extraction
- Context combination → RAG pipeline → Answer generation with citations
- Image reference & feedback tracking

**Coverage:**
- Image format & size validation
- Vision AI (Claude Vision / GPT-4) integration
- OCR text extraction (Tesseract / Cloud OCR)
- Duplicate detection (hash-based)
- Retention & auto-deletion policies

**Key Endpoints:**
```
POST   /api/v1/chat/image-query
GET    /api/v1/chat/images/{id}
```

---

#### UC-004: Session Management & History
**File:** [chat.md](chat.md) - Section 2

Complete conversation session lifecycle & management.

**Workflow:**
- Create session → Load history → Context window building
- Session expiration & archiving → Export & search

**Coverage:**
- Session lifecycle (active → archived → deleted)
- Context loading & history retrieval
- Last N messages strategy
- Session summarization (for long conversations)

**Key Endpoints:**
```
POST   /api/v1/chat/sessions
GET    /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{id}
PUT    /api/v1/chat/sessions/{id}
DELETE /api/v1/chat/sessions/{id}
GET    /api/v1/chat/sessions/{id}/search
POST   /api/v1/chat/sessions/{id}/export
```

---

#### UC-005: Feedback & Rating System
**File:** [chat.md](chat.md) - Section 7

Capture user feedback for quality improvement.

**Workflow:**
- Display rating UI → User provides rating/comment → Sentiment analysis
- Save feedback → Update message & session stats → Analytics logging

**Coverage:**
- Rating types (1-5 stars, thumbs up/down)
- Sentiment analysis on comments
- Category-based feedback (accurate, relevant, complete, etc.)
- Feedback analytics aggregation
- Quality metrics tracking

**Key Endpoints:**
```
POST   /api/v1/chat/feedback
GET    /api/v1/analytics/feedback
```

---

#### UC-006: User Profile & Personalization
**File:** [chat.md](chat.md) - Section 8

Personalize responses based on user profile (major, year, interests).

**Workflow:**
- Load user profile → Extract academic context
- Inject context into system prompt → Tailored responses

**Coverage:**
- Academic profile (major, year, specialization)
- User preferences (language, response length, etc.)
- Interests tracking
- Statistics & engagement metrics

**Key Endpoints:**
```
GET    /api/v1/users/profile
PUT    /api/v1/users/profile
GET    /api/v1/users/preferences
PUT    /api/v1/users/preferences
GET    /api/v1/users/statistics
```

---

### Admin Features (Knowledge Management)

#### UC-007: Document Ingestion & Upload
**File:** [ingestion.md](ingestion.md) - Section 2

Manual document upload with validation & quality checks.

**Workflow:**
- File upload → Validation → Parsing → Duplicate detection
- Store as PENDING → Add to approval queue

**Coverage:**
- File format support (Markdown, PDF, DOCX, HTML, TXT)
- Content validation & integrity checks
- Hash-based duplicate detection
- Metadata extraction
- Error handling & malware scanning

**Key Endpoints:**
```
POST   /api/v1/admin/documents/upload
POST   /api/v1/admin/documents/batch-upload
GET    /api/v1/admin/documents
GET    /api/v1/admin/documents/{id}
```

---

#### UC-008: Web Crawler & Data Synchronization
**File:** [ingestion.md](ingestion.md) - Section 3

Automated content ingestion from university websites.

**Workflow:**
- Scheduled trigger → Fetch URLs → Parse content → Hash-based change detection
- Create PENDING documents → Optional auto-approval → Processing

**Coverage:**
- Crawler configuration (scheduling, selectors, depth)
- Content fetching & parsing (Firecrawl, BeautifulSoup)
- Change detection strategy (hash, semantic similarity)
- Deduplication & versioning
- Retry & error recovery
- Crawl session logging

**Key Endpoints:**
```
POST   /api/v1/admin/crawlers
GET    /api/v1/admin/crawlers
PUT    /api/v1/admin/crawlers/{id}
GET    /api/v1/admin/crawlers/{id}/history
```

---

#### UC-009: Document Approval Workflow
**File:** [ingestion.md](ingestion.md) - Section 4

Quality control process before documents go live.

**Workflow:**
- PENDING documents → Admin dashboard → Content review → Diff viewer
- Approve/Reject decision → Processing pipeline (if approved) → Indexing

**Coverage:**
- Approval dashboard with queue management
- Diff viewer for updates
- Admin comments & audit trail
- Versioning & archiving
- Processing trigger

**Key Endpoints:**
```
GET    /api/v1/admin/approval/pending
GET    /api/v1/admin/approval/{id}/detail
GET    /api/v1/admin/approval/{id}/diff
POST   /api/v1/admin/approval/{id}/approve
POST   /api/v1/admin/approval/{id}/reject
GET    /api/v1/admin/approval/stats
```

---

#### UC-010: Document Processing Pipeline
**File:** [ingestion.md](ingestion.md) - Section 5

Transform approved documents into searchable vectors.

**Workflow:**
- Approved document → Chunking (300-500 tokens)
- Text cleaning & normalization → Embedding generation (Sentence Transformers)
- Vector indexing into Qdrant → MongoDB metadata update

**Coverage:**
- Chunk boundary preservation (paragraphs, sentences)
- Batch embedding (with GPU acceleration)
- Vector DB operations (upsert, delete, search)
- Quality checks & error recovery
- Performance optimization

**Key Endpoints:**
```
POST   /api/v1/admin/documents/{id}/process
GET    /api/v1/admin/processing-jobs/{id}
```

---

#### UC-011: Vector Database Management
**File:** [ingestion.md](ingestion.md) - Section 6

Manage Qdrant for semantic search.

**Workflow:**
- Vector upsert → Indexing → Search operations → Filtering & retrieval
- Maintenance: Optimization, backups, monitoring

**Coverage:**
- Qdrant configuration & collection setup
- HNSW index tuning
- Batch operations optimization
- Search quality & latency monitoring
- Health checks & recovery

---

#### UC-012: Document Versioning & History
**File:** [ingestion.md](ingestion.md) - Section 7

Track document versions & maintain audit trail.

**Workflow:**
- New version detected → Archive old → Create new PENDING
- Approval & indexing → Replace vectors with new version

**Coverage:**
- Version tracking (v1, v2, v3, etc.)
- Status transitions (PENDING → APPROVED → ARCHIVED)
- Change summary & diff
- Retention policies
- Search only finds current version

---

### Core Features (Chat & Ingestion)

#### Error Handling & Recovery (Both Subsystems)
**File:** [chat.md](chat.md) - Section 9 & [ingestion.md](ingestion.md) - Section 8

Comprehensive error strategies across all workflows.

**Coverage:**
- Input validation errors (400)
- Authentication errors (401/403)
- Resource not found (404)
- Service unavailable (5xx)
- Rate limiting (429)
- Circuit breaker patterns
- Retry strategies with exponential backoff
- Fallback mechanisms

---

#### Performance Optimization (Both Subsystems)
**File:** [chat.md](chat.md) - Section 10 & [ingestion.md](ingestion.md) - Section 10

Scaling, caching, and performance tuning.

**Coverage:**
- Multi-layer caching (Redis, in-memory, query results)
- Vertical & horizontal scaling strategies
- Database optimization (indexing, sharding, archival)
- SLA targets (P95 latencies)
- Monitoring & health checks
- Async processing patterns

---

## Missing Use Cases (Planned/Todo)

### HIGH PRIORITY - User Features

#### UC-013: Bookmark & Save Q&A
**Status:** PLANNED - Not yet documented

Allow users to save important Q&A pairs with custom tags & notes.

**Expected Workflow:**
- User clicks "Bookmark" on response → Save to personal collection
- Manage bookmarks: Tag, search, organize, export
- Create custom Q&A collections by topic

**Scope:**
- Bookmark data model
- CRUD operations
- Tag management & search
- Collections feature
- Export formats (PDF, JSON, CSV)

**API Endpoints (Expected):**
```
POST   /api/v1/bookmarks
GET    /api/v1/bookmarks
PUT    /api/v1/bookmarks/{id}
DELETE /api/v1/bookmarks/{id}
GET    /api/v1/bookmarks/search
POST   /api/v1/bookmarks/{id}/export
```

---

#### UC-014: Smart Suggestions & Related Questions
**Status:** PLANNED - Not yet documented

Recommend related questions or trending topics during conversations.

**Expected Workflow:**
- User asks question → System analyzes context
- Retrieve related Q&A from history & knowledge base
- Display "You might also want to know..." suggestions
- Track suggestion relevance & click-through rate

**Scope:**
- Similarity-based suggestion algorithm
- Trending topic detection
- Personalized recommendations (based on user major/interests)
- Analytics on suggestion effectiveness

---

### HIGH PRIORITY - Admin Features

#### UC-015: Admin Analytics & Dashboard
**Status:** PLANNED - Not yet documented

Comprehensive system analytics for administrators.

**Expected Workflow:**
- Admin opens dashboard → View metrics aggregation
- Drill down: Requests, latency, errors, user engagement
- Export reports (PDF, CSV)
- Set alerts on anomalies

**Scope:**
- Usage metrics (DAU/MAU, total requests, peak times)
- Performance metrics (response latency, cache hit rate, search quality)
- Cost tracking (token usage by provider, cost per query)
- User engagement metrics
- System health monitoring
- Real-time alerts

**API Endpoints (Expected):**
```
GET    /api/v1/admin/analytics/overview
GET    /api/v1/admin/analytics/usage
GET    /api/v1/admin/analytics/performance
GET    /api/v1/admin/analytics/costs
GET    /api/v1/admin/analytics/health
GET    /api/v1/admin/reports
POST   /api/v1/admin/reports/generate
```

---

#### UC-016: Feedback Analytics Dashboard (Admin)
**Status:** PLANNED - Not yet documented

Analyze user feedback for quality improvement.

**Expected Workflow:**
- Admin views feedback dashboard → See trends & common issues
- Filter by: Topic, rating, date range, category
- Identify low-confidence queries → Knowledge gap detection
- Create action items for content updates

**Scope:**
- Feedback aggregation & trend analysis
- Sentiment analysis on comments
- Issue categorization & frequency
- Knowledge gap identification
- Response quality scoring
- Content improvement recommendations

**API Endpoints (Expected):**
```
GET    /api/v1/admin/analytics/feedback/summary
GET    /api/v1/admin/analytics/feedback/trends
GET    /api/v1/admin/analytics/feedback/categories
GET    /api/v1/admin/analytics/knowledge-gaps
GET    /api/v1/admin/analytics/quality-metrics
```

---

#### UC-017: Cost & LLM Usage Tracking
**Status:** PLANNED - Not yet documented

Monitor LLM API costs across different providers.

**Expected Workflow:**
- System tracks token usage per LLM call
- Aggregate by: Provider (OpenAI, Anthropic, Google), Model, User, Time
- Admin views cost dashboard → Set budgets & alerts
- Export cost reports

**Scope:**
- Token counting per LLM call
- Cost calculation per provider/model
- Budget management & alerts
- Cost by user, session, topic
- Historical cost trends
- ROI analysis (cost vs user satisfaction)

**API Endpoints (Expected):**
```
GET    /api/v1/admin/analytics/costs/overview
GET    /api/v1/admin/analytics/costs/by-provider
GET    /api/v1/admin/analytics/costs/by-model
GET    /api/v1/admin/analytics/costs/by-user
POST   /api/v1/admin/budgets
GET    /api/v1/admin/budgets/{id}
```

---

#### UC-018: User Management & Engagement
**Status:** PLANNED - Not yet documented

Admin view user profiles, engagement metrics, and manage user access.

**Expected Workflow:**
- Admin searches for user → View profile & activity
- See: Query count, session history, feedback given, engagement score
- Manage: Ban user, reset profile, export user data
- Export user list with engagement metrics

**Scope:**
- User search & filtering
- User engagement metrics
- Activity timeline
- Profile management (ban, suspend, restore)
- Data export & GDPR compliance
- User segmentation analysis

**API Endpoints (Expected):**
```
GET    /api/v1/admin/users
GET    /api/v1/admin/users/{id}
PUT    /api/v1/admin/users/{id}
DELETE /api/v1/admin/users/{id}
GET    /api/v1/admin/users/{id}/activity
POST   /api/v1/admin/users/{id}/ban
GET    /api/v1/admin/users/export
```

---

#### UC-019: Conversation History Review (Admin)
**Status:** PLANNED - Not yet documented

Admin search & review user conversations for quality assurance or support.

**Expected Workflow:**
- Admin searches conversations by: User, date, topic, quality score
- View full conversation thread with metadata
- Flag for review, add admin notes
- Export conversation transcript

**Scope:**
- Conversation search & filtering
- Full conversation viewer with formatting
- Admin annotations & notes
- Flag system (low quality, offensive, etc.)
- Export & reporting
- Privacy considerations (user consent for admin review)

**API Endpoints (Expected):**
```
GET    /api/v1/admin/conversations/search
GET    /api/v1/admin/conversations/{id}
POST   /api/v1/admin/conversations/{id}/review
PUT    /api/v1/admin/conversations/{id}/note
```

---

## Use Case Summary Matrix

| UC ID | Name | Category | Status | Priority | Coverage |
|-------|------|----------|--------|----------|----------|
| UC-001 | Intelligent Chat with RAG | User | DONE | P0 | 100% |
| UC-002 | Voice Query Processing | User | DONE | P1 | 100% |
| UC-003 | Image Query Processing | User | DONE | P1 | 100% |
| UC-004 | Session Management | User | DONE | P0 | 100% |
| UC-005 | Feedback System | User | DONE | P2 | 100% |
| UC-006 | User Profile & Personalization | User | DONE | P1 | 100% |
| UC-007 | Document Upload | Admin | DONE | P0 | 100% |
| UC-008 | Web Crawler & Sync | Admin | DONE | P0 | 100% |
| UC-009 | Document Approval | Admin | DONE | P0 | 100% |
| UC-010 | Processing Pipeline | Admin | DONE | P0 | 100% |
| UC-011 | Vector DB Management | Admin | DONE | P0 | 100% |
| UC-012 | Document Versioning | Admin | DONE | P0 | 100% |
| UC-013 | Bookmarks & Save Q&A | User | PLANNED | P2 | 0% |
| UC-014 | Smart Suggestions | User | PLANNED | P2 | 0% |
| UC-015 | Analytics Dashboard | Admin | PLANNED | P1 | 0% |
| UC-016 | Feedback Analytics | Admin | PLANNED | P1 | 0% |
| UC-017 | Cost Tracking | Admin | PLANNED | P2 | 0% |
| UC-018 | User Management | Admin | PLANNED | P2 | 0% |
| UC-019 | Conversation Review | Admin | PLANNED | P2 | 0% |

---

## Documentation Structure

### Completed Use Cases Files:
- **chat.md** - All user-facing chat features (UC-001 to UC-006)
  - Sections: Session Management, Text Query, Voice Query, Image Query, History, Feedback, Profile
  - Total: ~2000 lines, 10+ diagrams, complete error handling

- **ingestion.md** - All data ingestion & admin features (UC-007 to UC-012)
  - Sections: Upload, Crawler, Approval, Processing, Vector DB, Versioning
  - Total: ~2500 lines, 15+ diagrams, complete monitoring

### Recommended Next Steps:

#### Phase 2 Documentation (Recommended):
1. **admin_analytics.md** - UC-015, UC-016, UC-017, UC-019
   - Dashboard design & metrics
   - Analytics pipelines
   - Cost tracking
   - Reports & exports

2. **bookmarks_and_suggestions.md** - UC-013, UC-014
   - Bookmark data model & operations
   - Suggestion algorithms
   - Trending topics detection
   - Personalization logic

3. **user_management.md** - UC-018
   - Admin user management
   - Engagement metrics
   - GDPR compliance

---

## Key Integration Points (All Use Cases)

```
Layer 1: Authentication (JWT)
  ↓
Layer 2: Request Validation & Routing
  ↓
Layer 3: Core Services (Chat, Ingestion, Analytics)
  ↓
Layer 4: Data Access Layer (MongoDB, Qdrant, MinIO, Redis)
  ↓
Layer 5: External Services (LLM, STT, Vision AI, Embeddings)
  ↓
Layer 6: Monitoring & Analytics Pipeline
```

---

## Best Practices Across All Use Cases

1. **Error Handling:** All use cases implement multi-layer error handling with fallbacks
2. **Performance:** P95 latency targets specified for each operation
3. **Scalability:** Horizontal & vertical scaling strategies defined
4. **Monitoring:** Real-time metrics & health checks for all services
5. **Security:** Authentication, authorization, PII handling, data retention
6. **Audit Trail:** All admin operations logged with timestamps & user IDs
7. **Graceful Degradation:** Services continue with reduced functionality on partial failures

---

## For Developers

**Before implementing any use case:**
1. Read the complete flow diagrams
2. Understand all error scenarios
3. Implement error handling first
4. Add monitoring/logging points
5. Consider edge cases from the documentation
6. Test with the example data models

**Performance targets are NOT optional** - they're SLA commitments to users.

**All APIs must:**
- Use JWT authentication
- Validate inputs thoroughly
- Return standard error codes
- Support rate limiting
- Log all important events
- Monitor response times

