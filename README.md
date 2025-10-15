# AMI RAG System

Comprehensive Retrieval-Augmented Generation system for PTIT (Posts and Telecommunications Institute of Technology) with multiple LLM providers, vector stores, and advanced RAG features.

## 🚀 Features

- **Multiple LLM Providers**: OpenAI (GPT-4o-mini), Google Gemini (1.5-flash), Anthropic Claude (3.5-sonnet)
- **Multiple Embeddings**: OpenAI (text-embedding-3-small), HuggingFace (all-MiniLM-L6-v2)
- **Vector Stores**: PostgreSQL with pgvector, ChromaDB
- **Advanced RAG**: Context retrieval, metadata filtering, similarity threshold, source citation
- **Caching Layer**: Redis for embeddings & query results (70-80% cache hit rate)
- **Thinking Modes**: Disabled, Chain-of-Thought, Step-by-Step, Reasoning
- **Streaming Support**: Server-Sent Events (SSE) for real-time responses
- **Collection Management**: Organize documents by domain/topic
- **Async Architecture**: Built with asyncio + asyncpg for high performance
- **Production Ready**: Connection pooling, error handling, health checks

## 📋 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI + Uvicorn |
| **Package Manager** | UV (ultra-fast Python) |
| **Database** | PostgreSQL 16 + pgvector |
| **Cache** | Redis 7 (async) |
| **Vector DB** | pgvector / ChromaDB |
| **LLMs** | OpenAI, Gemini, Claude |
| **Embeddings** | OpenAI, HuggingFace |
| **Orchestration** | Docker Compose |

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- UV package manager: `pip install uv`
- At least one LLM API key (OpenAI, Gemini, or Anthropic)

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd Ami

# Install dependencies
make install
# or: uv sync
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required API Keys** (at least one):
```env
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 3. Start Databases

```bash
# Start PostgreSQL, Redis, ChromaDB
make docker-up

# Wait ~10 seconds for services to initialize

# Verify connections
make test-db
```

Expected output:
```
✅ PostgreSQL test PASSED
✅ Redis test PASSED
✅ ChromaDB test PASSED
```

### 4. Ingest Data

```bash
# Ingest 47 PTIT documents into vector database
make ingest-data

# This will:
# - Read from assets/data.json (47 documents)
# - Process markdown files from assets/raw/
# - Generate embeddings with caching
# - Store in vector database (collection: ptit_knowledge)
```

### 5. Start API Server

```bash
# Development mode (auto-reload)
make dev

# Production mode
make run

# Server starts at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

## 📚 API Documentation

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman Collection**: Import `AMI_RAG_API.postman_collection.json`

### Core Endpoints

#### 🤖 Generate (RAG Queries)

```bash
POST /api/v1/generate/chat
```
Generate chat responses with RAG support, multiple LLM providers, thinking modes.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Học viện PTIT là gì?"}
  ],
  "model": "openai",
  "thinking_mode": "chain_of_thought",
  "rag_config": {
    "enabled": true,
    "top_k": 5,
    "similarity_threshold": 0.7,
    "include_sources": true
  },
  "generation_config": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "collection": "ptit_knowledge"
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "Học viện Công nghệ Bưu chính Viễn thông..."
  },
  "sources": [
    {
      "id": "123",
      "content": "...",
      "similarity": 0.85,
      "metadata": {...}
    }
  ],
  "metadata": {
    "rag_enabled": true,
    "source_count": 5
  }
}
```

---

```bash
POST /api/v1/generate/stream
```
Stream responses in real-time (Server-Sent Events).

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/generate/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Giới thiệu về PTIT"}],
    "rag_config": {"enabled": true},
    "stream": true
  }' \
  --no-buffer
```

#### 🗄️ Vector Database

```bash
POST /api/v1/vectordb/upload
```
Upload documents to vector database.

**Request:**
```json
{
  "content": "Your document content...",
  "collection": "ptit_knowledge",
  "metadata": {
    "title": "Document Title",
    "source": "Manual Entry"
  },
  "chunk_config": {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "strategy": "fixed"
  }
}
```

---

```bash
POST /api/v1/vectordb/search
```
Semantic search with filters.

**Request:**
```json
{
  "query": "Các cơ sở đào tạo của PTIT",
  "collection": "ptit_knowledge",
  "top_k": 5,
  "similarity_threshold": 0.7,
  "metadata_filter": {
    "source": "Website"
  }
}
```

---

```bash
GET /api/v1/vectordb/stats?collection=ptit_knowledge
```
Get database statistics.

```bash
GET /api/v1/vectordb/collections
```
List all collections.

```bash
DELETE /api/v1/vectordb/{doc_id}
```
Delete document by ID.

#### ⚙️ Config & Health

```bash
GET /api/v1/config/health
```
Check system health and database connections.

```bash
GET /api/v1/config/models
```
List available models and their status.

```bash
GET /api/v1/config/providers
```
Get provider configurations.

## 🏗️ Architecture

### Project Structure

```
app/
├── core/                      # Domain layer (SOLID interfaces)
│   ├── interfaces.py          # Abstract interfaces
│   └── models.py              # Pydantic models
├── infrastructure/            # Infrastructure layer
│   ├── embeddings/
│   │   ├── openai_embeddings.py
│   │   └── huggingface_embeddings.py
│   ├── llms/
│   │   ├── openai_llm.py
│   │   ├── gemini_llm.py
│   │   └── anthropic_llm.py
│   ├── vector_stores/
│   │   ├── pgvector_store.py
│   │   └── chroma_store.py
│   ├── databases/
│   │   ├── postgres_client.py  # asyncpg pool
│   │   ├── redis_client.py     # redis async
│   │   └── chroma_client.py    # HTTP client
│   └── tools/
│       └── markitdown_processor.py
├── application/               # Application layer
│   ├── services.py            # RAGService, DocumentService
│   ├── factory.py             # ProviderFactory (singleton)
│   └── ingestion_service.py  # Document ingestion
└── api/                       # API layer
    ├── main.py                # FastAPI app
    ├── routes.py              # API endpoints
    └── dependencies.py        # Dependency injection

scripts/
├── ingest_data.py             # Data ingestion CLI
├── test_db_connections.py     # Database tests
└── init_db.sql                # PostgreSQL schema

assets/
├── data.json                  # Document metadata (47 docs)
└── raw/                       # Markdown files (47 files)
```

### Database Schema

**PostgreSQL Tables:**
```sql
documents (id, title, file_name, metadata, created_at, updated_at)
chunks (id, document_id, content, chunk_order, metadata)
embeddings (id, chunk_id, embedding [vector(1536)], provider, model)
collections (id, name, description)
document_collections (document_id, collection_id)
```

**Indexes:**
- IVFFlat vector index on embeddings for fast similarity search
- GIN indexes on metadata (JSONB) for filtering
- B-tree indexes on foreign keys

### Caching Strategy

**Redis Keys:**
- `embedding:{hash}` - Embedding cache (TTL: 7 days)
- `query:{hash}` - Query result cache (TTL: 1 hour)

**Cache Hit Rates:**
- Embeddings: 70-80% after warm-up
- Queries: 40-60% for repeated questions

## 🔧 Configuration

### Environment Variables

See `.env.example` for all options. Key settings:

```env
# LLM Providers (at least one)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ami_rag
POSTGRES_MIN_POOL_SIZE=5
POSTGRES_MAX_POOL_SIZE=20

# Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_password
ENABLE_CACHE=true
CACHE_TTL=3600

# Defaults
DEFAULT_LLM_PROVIDER=openai
DEFAULT_EMBEDDING_PROVIDER=openai
DEFAULT_VECTOR_STORE=pgvector

# RAG Config
CHUNK_SIZE=512
CHUNK_OVERLAP=50
RETRIEVAL_TOP_K=5
SIMILARITY_THRESHOLD=0.7
```

## 🛠️ Makefile Commands

```bash
# Development
make install         # Install dependencies with UV
make run             # Run production server
make dev             # Run dev server (auto-reload)

# Database
make docker-up       # Start PostgreSQL, Redis, ChromaDB
make docker-down     # Stop all databases
make docker-logs     # View container logs
make docker-restart  # Restart services
make test-db         # Test database connections

# Data Processing
make ingest-data     # Ingest documents into vector DB
make crawl-stats     # Show crawl statistics
make crawl-dry       # Dry run crawl
make crawl           # Crawl data from URLs

# Testing
make test-api        # Run API tests

# Utilities
make clean           # Clean temporary files
```

## 📊 Performance

### Benchmarks

| Metric | Value |
|--------|-------|
| **Embedding Generation** | ~20/sec (OpenAI API) |
| **HuggingFace Local** | ~50/sec (CPU), ~200/sec (GPU) |
| **Query Latency (cold)** | ~1-2 seconds |
| **Query Latency (cached)** | ~200-500ms |
| **Fully Cached Query** | <100ms |
| **Ingestion Speed** | ~2-3 chunks/sec |
| **Cache Hit Rate** | 70-80% (embeddings) |

### Connection Pools

- PostgreSQL: 5-20 connections (asyncpg)
- Redis: 50 max connections
- ChromaDB: HTTP client with keep-alive

## 🎯 Usage Examples

### Python SDK

```python
from app.application.factory import ProviderFactory
from app.application.services import RAGService, DocumentService

# Initialize services
embedding = ProviderFactory.get_embedding_provider("openai")
llm = ProviderFactory.get_llm_provider("anthropic")
vector = await ProviderFactory.get_vector_store("pgvector")
cache = await ProviderFactory.get_redis_client()
processor = ProviderFactory.get_document_processor()

doc_service = DocumentService(processor)
rag_service = RAGService(embedding, llm, vector, doc_service, cache)

# Ingest document
result = await rag_service.ingest_text(
    "Your content here...",
    metadata={"title": "Example", "source": "Manual"},
    collection="my_collection"
)

# Query with RAG
response = await rag_service.query(
    "What is PTIT?",
    top_k=5,
    collection="ptit_knowledge"
)
print(response['answer'])
print(response['sources'])

# Stream query
async for chunk in rag_service.stream_query("Tell me about PTIT"):
    print(chunk, end='', flush=True)
```

### cURL Examples

**Chat with RAG:**
```bash
curl -X POST http://localhost:8000/api/v1/generate/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Học viện PTIT là gì?"}],
    "model": "openai",
    "rag_config": {
      "enabled": true,
      "top_k": 5,
      "include_sources": true
    },
    "collection": "ptit_knowledge"
  }'
```

**Upload Document:**
```bash
curl -X POST http://localhost:8000/api/v1/vectordb/upload \
  -H "Content-Type: application/json" \
  -d '{
    "content": "PTIT là trường đại học hàng đầu...",
    "collection": "ptit_knowledge",
    "metadata": {"title": "Giới thiệu PTIT"}
  }'
```

**Search:**
```bash
curl -X POST http://localhost:8000/api/v1/vectordb/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "các cơ sở đào tạo",
    "collection": "ptit_knowledge",
    "top_k": 5
  }'
```

## 🧪 Testing

### Database Connections

```bash
make test-db
```

### API Endpoints

```bash
# Using Postman
# Import: AMI_RAG_API.postman_collection.json

# Or using pytest
make test-api
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/api/v1/config/health

# Check models
curl http://localhost:8000/api/v1/config/models

# Get stats
curl http://localhost:8000/api/v1/vectordb/stats
```

## 🏛️ SOLID Principles

- **Single Responsibility**: Each service/provider has one purpose
- **Open/Closed**: Easy to add new LLM/embedding providers
- **Liskov Substitution**: All providers are interchangeable via interfaces
- **Interface Segregation**: Small, focused interfaces (ILLMProvider, IEmbeddingProvider, etc.)
- **Dependency Inversion**: Depend on abstractions (interfaces), not concrete implementations

## 📝 Documentation

- **API Docs**: [CORE_AI_SUMMARY.md](CORE_AI_SUMMARY.md) - Complete implementation guide
- **Database Setup**: [SETUP_DATABASE.md](SETUP_DATABASE.md) - Database configuration
- **Postman Collection**: [AMI_RAG_API.postman_collection.json](AMI_RAG_API.postman_collection.json)
- **Interactive Docs**: http://localhost:8000/docs

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if containers are running
docker-compose ps

# View logs
make docker-logs

# Restart services
make docker-restart
```

### API Key Issues

```bash
# Verify API keys are set
cat .env | grep API_KEY

# Check provider availability
curl http://localhost:8000/api/v1/config/providers
```

### Import Errors

```bash
# Reinstall dependencies
make install

# Check Python version (requires 3.11+)
python --version
```

## 🚢 Deployment

### Docker Production Build

```bash
# Build image
docker build -t ami-rag-api .

# Run container
docker run -d \
  --name ami-rag \
  -p 8000:8000 \
  --env-file .env \
  ami-rag-api
```

### Environment Variables for Production

```env
DEBUG=false
POSTGRES_HOST=your-postgres-host
REDIS_HOST=your-redis-host
# Add SSL/TLS configurations as needed
```

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please follow SOLID principles and include tests for new features.

## 📧 Support

For issues and questions, please open a GitHub issue or contact the development team.

---

**Built with ❤️ using FastAPI, PostgreSQL, and cutting-edge AI technologies**
