# Schema do Banco de Dados - CartaOS v2

## 1. Visão Geral

O schema do banco de dados foi projetado para ser relacional, robusto e escalável, utilizando **PostgreSQL**. A escolha pelo PostgreSQL se deve à sua confiabilidade, ao seu rico conjunto de funcionalidades e, crucialmente, ao suporte a extensões poderosas como a `pgvector`, que nos permite integrar a busca por similaridade vetorial diretamente no banco de dados principal, simplificando a arquitetura inicial.

Os princípios de design incluem:
*   **Normalização:** Evitar a redundância de dados sempre que possível.
*   **Integridade Referencial:** Usar chaves estrangeiras (`FOREIGN KEY`) para garantir a consistência entre as tabelas.
*   **Escalabilidade:** Utilizar UUIDs como chaves primárias para a maioria das tabelas principais, o que facilita a distribuição e a fusão de bancos de dados no futuro.
*   **Segurança:** Não armazenar dados sensíveis (como senhas ou chaves de API) em texto plano.

## 2. Extensões Necessárias

Antes de criar as tabelas, as seguintes extensões do PostgreSQL devem ser ativadas:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Para geração de UUIDs
CREATE EXTENSION IF NOT EXISTS vector;      -- Para o tipo de dado VECTOR (pgvector)
```

## 3. Schema Detalhado das Tabelas

### Tabela: `users`
Armazena as informações essenciais de cada usuário registrado.

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Armazena o hash da senha (ex: bcrypt)
    full_name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    subscription_id INT NOT NULL REFERENCES subscriptions(subscription_id) ON DELETE RESTRICT
);
```

### Tabela: `subscriptions`
Define os diferentes níveis de assinatura disponíveis no sistema.

```sql
CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL, -- 'Free', 'Researcher', 'Lab'
    price_monthly DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    processing_quota_monthly INT, -- NULL para ilimitado
    max_team_members INT DEFAULT 1,
    allow_cloud_sync BOOLEAN NOT NULL DEFAULT FALSE,
    allow_rag_chat BOOLEAN NOT NULL DEFAULT FALSE
);
```

### Tabela: `documents`
Armazena os metadados principais de cada documento pertencente a um usuário.

```sql
CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, -- Se o usuário for deletado, seus documentos também são.
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    cloud_storage_path VARCHAR(1024), -- Caminho no GCS/S3 para usuários premium
    local_storage_path VARCHAR(1024), -- Caminho no disco local para usuários do plano gratuito
    processing_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'error'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tabela: `document_semantic_metadata`
Armazena os dados enriquecidos gerados pelo pipeline de IA.

```sql
CREATE TABLE document_semantic_metadata (
    metadata_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    summary TEXT,
    key_concepts TEXT[], -- Armazena como um array de strings
    tags TEXT[],
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tabela: `document_chunks_and_vectors`
Armazena os "chunks" (pedaços de texto) de cada documento e seus respectivos embeddings vetoriais para a funcionalidade de RAG (Chat com Documentos).

```sql
CREATE TABLE document_chunks_and_vectors (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL, -- O pedaço de texto original
    page_number INT,
    embedding VECTOR(768) NOT NULL, -- A dimensão (768) depende do modelo de embedding utilizado
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar um índice para busca vetorial eficiente
CREATE INDEX ON document_chunks_and_vectors USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

### Tabela: `plugins`
Define os plugins disponíveis no marketplace.

```sql
CREATE TABLE plugins (
    plugin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    developer_id UUID NOT NULL REFERENCES users(user_id), -- O usuário que desenvolveu o plugin
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    version VARCHAR(20),
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    is_public BOOLEAN NOT NULL DEFAULT FALSE, -- Se está visível no marketplace
    review_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tabela: `user_plugins`
Tabela de associação que registra quais usuários compraram/instalaram quais plugins.

```sql
CREATE TABLE user_plugins (
    user_plugin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    plugin_id UUID NOT NULL REFERENCES plugins(plugin_id) ON DELETE CASCADE,
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, plugin_id) -- Garante que um usuário só pode instalar um plugin uma vez
);
```
