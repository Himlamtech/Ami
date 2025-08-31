-- Initialize AmiAgent Database with pgvector extension
-- This script runs automatically when PostgreSQL container starts

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for the application
CREATE SCHEMA IF NOT EXISTS amiagent;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA amiagent TO rag;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA amiagent TO rag;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA amiagent TO rag;

-- Set default search path
ALTER ROLE rag SET search_path TO amiagent, public;

-- Create example table for vector storage (will be created by application later)
-- This is just to verify pgvector is working
CREATE TABLE IF NOT EXISTS amiagent.vector_test (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on vector column for efficient similarity search
CREATE INDEX IF NOT EXISTS vector_test_embedding_idx
ON amiagent.vector_test
USING hnsw (embedding vector_cosine_ops);

-- Insert a test vector to verify everything works
INSERT INTO amiagent.vector_test (content, embedding)
VALUES ('test', ARRAY[0.1, 0.2, 0.3]::vector(3))
ON CONFLICT DO NOTHING;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'AmiAgent database initialized successfully with pgvector extension';
END $$;
