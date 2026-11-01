-- Tabela de Planos Operacionais com isolamento por nicho
CREATE TABLE IF NOT EXISTS planos_operacionais (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nicho TEXT NOT NULL,
    status TEXT DEFAULT 'PENDENTE',
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice parcial otimizado para consultas instantâneas e custo zero de I/O
CREATE INDEX IF NOT EXISTS idx_planos_pendentes_nicho 
ON planos_operacionais (nicho, created_at ASC) 
WHERE status = 'PENDENTE';

-- Tabela de Auditoria Financeira (Revenue Gate)
CREATE TABLE IF NOT EXISTS audit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    amount NUMERIC(10,2) NOT NULL,
    channel TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
