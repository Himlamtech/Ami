# Project: AMI (Advanced Management Interface)

**PTIT Intelligent Assistant - RAG-Powered Chatbot System**

---

## 📋 Use Cases

### 1. **Chat (Question Answering)**
- **Input Types:**
  - Text (primary)
  - Files (PDF, DOCX, TXT, MD, CSV, JSON)
  - Images (via gpt-5-nano Vision)
  - **Voice (Speech-to-Text with Wav2Vec2)** ✨ NEW!

- **Thinking Modes:**
  - **Fast**: Quick responses for simple queries (gpt-4.1-nano)
  - **Balance**: Optimal speed/quality ratio - *Default* (gpt-4.1-mini)
  - **Thinking**: Deep reasoning for complex questions (o4-mini)

- **Features:**
  - Chat History (auto-save sessions)
  - Web Search (optional, via Firecrawl API)
  - RAG-powered responses with source citations
  - Streaming responses
  - **Multi-turn conversations with context awareness** ✨ NEW!
    - Bot remembers previous messages
    - Understands references ("it", "that", "the previous one")
    - Auto-loads last 10 messages from database
    - Works with both streaming and non-streaming responses

### 2. **Data Management**
- **Operations:**
  - **Add**: Upload files, web scraping, web crawling
  - **View**: Statistics, collections, document metadata
  - **Delete**: Soft delete with restore capability
  - **Re-indexing**: Update vector embeddings

- **Data Sources:**
  - File Upload (drag & drop)
  - Web Scraper (single page)
  - Web Crawler (multi-page with depth control)

---

## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI (Python 3.12)
- **Architecture**: Clean Architecture + SOLID principles
- **API**: RESTful API with OpenAPI/Swagger docs

### **Frontend**
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Styling**: Custom CSS (Charter font)

### **AI/ML Models**
- **LLM Provider**: OpenAI
  - Fast Mode: `gpt-4.1-nano`
  - Balance Mode: `gpt-4.1-mini`
  - Thinking Mode: `o4-mini`
- **Embeddings**: HuggingFace
  - Model: `dangvantuan/vietnamese-document-embedding`
- **Image Generation**: gpt-5-nano
- **Vision Analysis**: gpt-5-nano
- **Speech-to-Text**: Wav2Vec2 (Vietnamese)
  - Base Model: `wav2vec2-base-vi-vlsp2020` (faster)
  - Large Model: `wav2vec2-large-vi-vlsp2020` (better accuracy)

### **Databases**
- **Vector Database**: Qdrant (semantic search)
- **Document Database**: MongoDB (users, metadata, chat history)
- **Cache**: Redis (response caching, TTL: 3600s)
- **File Storage**: MinIO (S3-compatible object storage)

### **External APIs**
- **OpenAI API**: LLM, image generation
- **Firecrawl API**: Web scraping and crawling
- **HuggingFace**: Vietnamese text embeddings

### **Document Processing**
- **Library**: MarkItDown (Microsoft)
- **Supported Formats**: PDF, DOCX, TXT, MD, CSV, JSON, HTML
---

## 🏗️ Infrastructure

### **Architecture Pattern**
```
┌─────────────────────────────────────────┐
│           Frontend (React)              │
│         Port: 6009 (Dev/Prod)           │
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│         Backend (FastAPI)               │
│            Port: 6008                   │
└─────┬───────┬───────┬──────────┬────────┘
      │       │       │          │
┌─────▼──┐ ┌──▼───┐ ┌▼──────┐ ┌─▼──────┐
│ Qdrant │ │MongoDB│ │ Redis │ │ MinIO  │
│  6333  │ │ 27017 │ │ 6379  │ │  9000  │
└────────┘ └───────┘ └───────┘ └────────┘
```

### **Ports**
- **Frontend**: `6009` (Vite dev server)
- **Backend**: `6008` (FastAPI/Uvicorn)
- **MongoDB**: `27017`
- **Redis**: `6379`
- **Qdrant**: `6333` (HTTP), `6334` (gRPC)
- **MinIO**: `9000` (API), `9001` (Console)

### **Authentication**
- **Method**: JWT (JSON Web Tokens)
- **Algorithm**: HS256
- **Token Expiry**: 1440 minutes (24 hours)
- **Protected Routes**: All except login

### **CORS Configuration**
- Allowed Origins: `localhost:6009`, `localhost:6010`, `localhost:6008`
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Authorization, Content-Type

---

### **Docker Configuration**
- **Base Image**: `python:3.12-slim`
- **Multi-stage Build**: Yes (builder + production)
- **Health Check**: `/api/v1/config/health` (30s interval)
- **Non-root User**: `ami` (UID: 1000)

### **Environment Variables**
```env
# OpenAI
OPENAI_API_KEY=sk-...

# Firecrawl
FIRECRAWL_API_KEY=fc-...

# MongoDB
MONGO_USER=admin
MONGO_PASSWORD=***
MONGO_DB=ami_db

# JWT
JWT_SECRET_KEY=***

# MinIO
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=***
```

---

---

## 🔧 API Endpoints

### **Authentication**
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration (admin only)
- `GET /api/v1/auth/me` - Get current user

### **Chat**
- `POST /api/v1/generate/chat` - Generate chat response
- `GET /api/v1/chat-history/sessions` - List chat sessions
- `POST /api/v1/chat-history/sessions` - Create session
- `GET /api/v1/chat-history/sessions/{id}` - Get session details
- `DELETE /api/v1/chat-history/sessions/{id}` - Delete session

### **Data Management**
- `POST /api/v1/vectordb/ingest` - Ingest documents
- `POST /api/v1/vectordb/upload` - Upload files
- `POST /api/v1/crawl/scrape` - Scrape single page
- `POST /api/v1/crawl/crawl` - Crawl multiple pages
- `GET /api/v1/vectordb/stats` - Get database statistics
- `GET /api/v1/vectordb/collections` - List collections

### **Configuration**
- `GET /api/v1/config/health` - Health check
- `GET /api/v1/config/models` - List available models

### **File Storage (MinIO)**
- `POST /api/v1/images/upload` - Upload images/files
- MinIO Console: http://localhost:9001
- S3-compatible API: http://localhost:9000

### **Speech-to-Text (STT)**
- `POST /api/v1/stt/transcribe` - Transcribe audio to text
- `GET /api/v1/stt/health` - STT health check
- `GET /api/v1/stt/models` - List available STT models
- `GET /api/v1/stt/capabilities` - Get STT capabilities

---

## 📦 MinIO Setup

### Quick Start

```bash
# 1. Start MinIO container
docker compose up -d minio

# 2. Initialize MinIO (create bucket, test connection)
python scripts/init_minio.py

# 3. Run comprehensive tests (11 tests)
python test_minio_comprehensive.py
```

### Features

- ✅ **Upload Files**: Images, documents, any binary data
- ✅ **Download Files**: By object name or pre-signed URL
- ✅ **File Management**: Check existence, get info, list files
- ✅ **Copy Files**: Duplicate within bucket
- ✅ **Delete Files**: Remove files permanently
- ✅ **Pre-signed URLs**: Temporary public access (time-limited)
- ✅ **Bucket Statistics**: Total files, storage usage
- ✅ **Health Check**: Connection and permission verification

### Performance

- Upload Speed: ~20 MB/s (localhost)
- Download Speed: ~20 MB/s (localhost)
- Large File Support: Tested up to 10MB+
- Latency: <10ms for most operations

### Documentation

See [MINIO_SETUP_GUIDE.md](./MINIO_SETUP_GUIDE.md) for:
- Detailed setup instructions
- Python SDK usage examples
- Troubleshooting guide
- Security best practices
- Monitoring and metrics

---

## 🎤 Speech-to-Text (STT) Setup

### Quick Start

```bash
# 1. Install dependencies
pip install transformers torchaudio pyctcdecode librosa soundfile

# 2. Initialize STT (downloads model ~1-2 GB)
python scripts/init_stt.py

# 3. Run comprehensive tests (7 tests)
python test_stt_comprehensive.py
```

### Features

- 🇻🇳 **Vietnamese Optimized**: VLSP2020 trained models
- 🎯 **High Accuracy**: Language Model support
- ⚡ **Fast Processing**: ~0.5-1x realtime (CPU)
- 🎵 **Multi-format**: WAV, MP3, M4A, FLAC, OGG, OPUS, WebM
- 🔄 **Auto Resample**: Automatic 16kHz conversion
- 💾 **Lazy Loading**: Models load on first use
- 🖥️ **GPU Support**: Auto-detects CUDA

### Models

| Model | Speed | Accuracy | RAM | Recommended |
|-------|-------|----------|-----|-------------|
| **Base** | Fast | Good | 2 GB | ✅ Yes |
| **Large** | Slower | Better | 4 GB | For difficult audio |

### Performance

- **Base Model**: ~0.5-1.0x realtime (CPU)
- **Large Model**: ~1.0-2.0x realtime (CPU)
- **With GPU**: 3-5x faster

### Documentation

See [STT_SETUP_GUIDE.md](./STT_SETUP_GUIDE.md) for:
- Complete setup guide
- Python SDK usage examples
- API documentation
- Troubleshooting guide
- Performance benchmarks
- Production checklist

---