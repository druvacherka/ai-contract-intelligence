-- ============================================
-- AI Contract Intelligence — Supabase Schema
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Users profile table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'member',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contracts table — stores uploaded contracts and analysis results
CREATE TABLE IF NOT EXISTS public.contracts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    filename TEXT NOT NULL,
    document_type TEXT,
    pages INTEGER DEFAULT 0,
    processing_method TEXT,
    ocr_confidence FLOAT,
    clean_text TEXT,
    text_preview TEXT,

    -- NLP Analysis Results
    primary_clause TEXT,
    primary_confidence FLOAT,
    overall_risk_score INTEGER DEFAULT 0,
    overall_risk_level TEXT DEFAULT 'Low',
    completeness_score INTEGER DEFAULT 0,

    -- AI Summary
    ai_summary TEXT,
    key_findings JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',

    -- Detailed Analysis
    entities JSONB DEFAULT '{}',
    clauses JSONB DEFAULT '[]',
    clause_risks JSONB DEFAULT '[]',
    risk_factors JSONB DEFAULT '[]',
    missing_clauses JSONB DEFAULT '[]',

    -- Metadata
    file_size_mb FLOAT,
    processing_time_seconds FLOAT,
    agent_logs JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector embeddings for semantic search
CREATE TABLE IF NOT EXISTS public.contract_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    contract_id UUID REFERENCES public.contracts(id) ON DELETE CASCADE,
    chunk_index INTEGER DEFAULT 0,
    chunk_text TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast vector similarity search
CREATE INDEX IF NOT EXISTS contract_embeddings_embedding_idx
ON public.contract_embeddings
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Index on user_id for fast contract lookups
CREATE INDEX IF NOT EXISTS contracts_user_id_idx ON public.contracts(user_id);
CREATE INDEX IF NOT EXISTS contracts_created_at_idx ON public.contracts(created_at DESC);

-- ============================================
-- Row Level Security (RLS)
-- ============================================

ALTER TABLE public.contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contract_embeddings ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Contracts policies
CREATE POLICY "Users can view own contracts" ON public.contracts
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own contracts" ON public.contracts
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own contracts" ON public.contracts
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own contracts" ON public.contracts
    FOR DELETE USING (auth.uid() = user_id);

-- Embeddings policies
CREATE POLICY "Users can view own embeddings" ON public.contract_embeddings
    FOR SELECT USING (
        contract_id IN (SELECT id FROM public.contracts WHERE user_id = auth.uid())
    );
CREATE POLICY "Users can insert own embeddings" ON public.contract_embeddings
    FOR INSERT WITH CHECK (
        contract_id IN (SELECT id FROM public.contracts WHERE user_id = auth.uid())
    );

-- Service role bypass for backend operations
CREATE POLICY "Service role full access contracts" ON public.contracts
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access profiles" ON public.profiles
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access embeddings" ON public.contract_embeddings
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- Functions
-- ============================================

-- Semantic search function
CREATE OR REPLACE FUNCTION search_contracts(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 10,
    p_user_id UUID DEFAULT NULL
)
RETURNS TABLE (
    contract_id UUID,
    chunk_text TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ce.contract_id,
        ce.chunk_text,
        1 - (ce.embedding <=> query_embedding) AS similarity
    FROM public.contract_embeddings ce
    JOIN public.contracts c ON ce.contract_id = c.id
    WHERE (p_user_id IS NULL OR c.user_id = p_user_id)
      AND 1 - (ce.embedding <=> query_embedding) > match_threshold
    ORDER BY ce.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Auto-create profile on signup trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email, avatar_url)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', ''),
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'avatar_url', NEW.raw_user_meta_data->>'picture', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger (drop first if exists)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
