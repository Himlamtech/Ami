-- Initialize database for AMI RAG System
-- PostgreSQL with pgvector extension
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
-- Documents table: stores metadata about original documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    file_name TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_documents_file_name ON documents(file_name);
CREATE INDEX idx_documents_metadata ON documents USING GIN(metadata);
-- Chunks table: stores text chunks from documents
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_chunk_index ON chunks(chunk_index);
-- Embeddings table: stores vector embeddings for chunks
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    embedding vector(1536),
    -- OpenAI ada-002/text-embedding-3-small
    provider TEXT NOT NULL,
    -- 'openai', 'huggingface'
    model TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chunk_id, provider, model)
);
CREATE INDEX idx_embeddings_chunk_id ON embeddings(chunk_id);
CREATE INDEX idx_embeddings_provider_model ON embeddings(provider, model);
-- Vector similarity search index (IVFFlat for better performance)
-- Using cosine distance for similarity
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_cosine ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- Alternative: HNSW index (more accurate but slower to build)
-- CREATE INDEX IF NOT EXISTS idx_embeddings_vector_hnsw 
-- ON embeddings USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 64);
-- Collections table: for organizing documents into collections
CREATE TABLE IF NOT EXISTS collections (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Document-Collection mapping (many-to-many)
CREATE TABLE IF NOT EXISTS document_collections (
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (document_id, collection_id)
);
CREATE INDEX idx_document_collections_document ON document_collections(document_id);
CREATE INDEX idx_document_collections_collection ON document_collections(collection_id);
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ language 'plpgsql';
-- Trigger for documents table
CREATE TRIGGER update_documents_updated_at BEFORE
UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- Default collection for all documents
INSERT INTO collections (name, description)
VALUES (
        'default',
        'Default collection for all documents'
    ) ON CONFLICT (name) DO NOTHING;
-- Success message
DO $$ BEGIN RAISE NOTICE 'Database initialized successfully with pgvector extension!';
END $$;