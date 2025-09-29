# Arquitetura do Sistema - CartaOS v2

## 1. Princípios de Arquitetura

A arquitetura da nova versão do CartaOS é guiada pelos seguintes princípios:

*   **Multiplataforma (Platform Agnostic):** A arquitetura deve suportar de forma nativa e eficiente a execução em Desktops (Windows, macOS, Linux), Web e Dispositivos Móveis (iOS, Android) a partir de uma base de código unificada sempre que possível.
*   **Escalabilidade:** O backend deve ser projetado para escalar horizontalmente, suportando desde um único usuário no plano gratuito até milhares de usuários concorrentes em planos de equipe e institucionais.
*   **Segurança:** A segurança dos dados do usuário, especialmente seu conteúdo de pesquisa e chaves de API, é primordial. A arquitetura deve incorporar princípios de segurança desde o design (Security by Design).
*   **Separation of Concerns:** Há uma clara divisão de responsabilidades entre o cliente (Frontend), que lida com a interface e a experiência do usuário, e o servidor (Backend), que gerencia a lógica de negócios, os dados e o processamento pesado.
*   **Modelo Híbrido (Local-First & Cloud-Enhanced):** A aplicação deve funcionar de forma útil offline (processamento local para o plano gratuito), mas ser aprimorada com funcionalidades de nuvem (sincronização, processamento pesado, colaboração) para os planos pagos.

## 2. Diagrama de Arquitetura de Alto Nível (C4 Model - Nível 1)

O diagrama abaixo descreve os principais contêineres do sistema e suas interações.

```mermaid
graph TD
    subgraph "Usuário Final"
        U(Pesquisador Acadêmico)
    end

    subgraph "Ecossistema CartaOS"
        C[Cliente Multiplataforma<br>(Flutter)]
        B[Backend API<br>(Go / FastAPI)]
        DB[(Banco de Dados<br>PostgreSQL + pgvector)]
        S3[(Armazenamento de Arquivos<br>Cloud Storage)]
        AI_Services(Serviços de IA Externos<br>Google Gemini API)
        Auth(Serviço de Autenticação<br>Firebase Auth)
    end

    U -- "Usa" --> C
    C -- "Faz chamadas de API (HTTPS)" --> B
    C -- "Autenticação" --> Auth
    B -- "Lê/Escreve dados do usuário" --> DB
    B -- "Armazena/Recupera arquivos" --> S3
    B -- "Chama para análise semântica" --> AI_Services
    B -- "Valida tokens" --> Auth
```

## 3. Detalhamento dos Componentes

### 3.1. Frontend (Cliente Multiplataforma)

*   **Tecnologia:** Flutter & Dart.
*   **Responsabilidades:**
    *   **Interface do Usuário (UI):** Renderizar toda a interface do usuário de forma consistente em todas as plataformas.
    *   **Gerenciamento de Estado:** Gerenciar o estado da aplicação (documentos carregados, status da UI, perfil do usuário) usando um padrão como BLoC ou Riverpod.
    *   **Comunicação com o Backend:** Realizar chamadas seguras (HTTPS) para a API do backend para buscar dados, disparar processamentos e sincronizar informações.
    *   **Processamento Local (Modo Gratuito):** Para usuários do plano gratuito, o cliente Flutter pode invocar processos locais (scripts Python ou binários de OCR) para realizar a análise de documentos diretamente na máquina do usuário, sem sobrecarregar o backend.
    *   **Segurança:** Armazenar de forma segura tokens de autenticação, chaves de API e outros segredos usando `flutter_secure_storage`.
    *   **Persistência Local:** Utilizar um banco de dados local (como SQLite/Drift ou Hive) para cache de metadados e para permitir o funcionamento offline.

### 3.2. Backend (Servidor)

*   **Tecnologia:** Go (Recomendado para performance e concorrência) ou Python com FastAPI.
*   **Arquitetura Interna:** Arquitetura de microsserviços ou um monólito modular, com cada domínio de negócio (autenticação, documentos, plugins) em seu próprio módulo.
*   **Responsabilidades:**
    *   **API Gateway:** Expor uma API RESTful ou GraphQL segura para ser consumida pelos clientes.
    *   **Serviço de Usuários e Autenticação:** Gerenciar perfis de usuário, planos de assinatura e integração com um serviço de autenticação como Firebase Auth para lidar com o registro e login.
    *   **Serviço de Documentos:** Gerenciar os metadados dos documentos, o status do processamento e os caminhos para os arquivos no armazenamento de objetos.
    *   **Serviço de Processamento (Worker):** Um serviço assíncrono (usando filas de mensagens como RabbitMQ ou Google Pub/Sub) que executa o pipeline de processamento pesado para usuários premium (OCR, análise estrutural, enriquecimento com IA). Isso garante que a API principal permaneça responsiva.
    *   **Serviço de Busca Semântica (RAG):** Lidar com as queries do "Chat com Documentos", convertendo a pergunta do usuário em um vetor, buscando chunks relevantes no banco de dados vetorial e usando um LLM para sintetizar a resposta.
    *   **Serviço de Marketplace:** Conter a lógica de negócios para o marketplace de plugins, incluindo submissão, aprovação e compra de plugins.

### 3.3. Arquitetura de Dados

*   **Banco de Dados Relacional (PostgreSQL):**
    *   **Uso:** Armazenar dados estruturados e relacionais: informações de usuários, assinaturas, metadados de documentos, informações de plugins.
    *   **Extensão `pgvector`:** Adiciona capacidades de busca de similaridade vetorial diretamente no PostgreSQL, permitindo que ele funcione como um banco de dados vetorial para a funcionalidade de RAG. Isso simplifica a stack, evitando a necessidade de um banco de dados vetorial separado (como ChromaDB ou Pinecone) nas fases iniciais.

*   **Armazenamento de Objetos (Cloud Storage - GCS/S3):**
    *   **Uso:** Armazenar os arquivos binários (os PDFs originais dos usuários premium). Os arquivos não são armazenados no banco de dados.
    *   **Acesso:** O acesso aos arquivos será feito através de URLs assinadas (signed URLs) geradas pelo backend, garantindo que apenas o proprietário do documento possa acessá-lo por um tempo limitado.

## 4. Fluxo de Dados de Processamento (Plano Premium)

1.  O **Cliente Flutter** solicita ao **Backend API** uma URL de upload para um novo documento.
2.  O Cliente faz o upload do arquivo PDF diretamente para o **Cloud Storage** usando a URL assinada.
3.  Após o upload, o Cliente notifica a API, que cria uma entrada para o documento no **PostgreSQL** com o status "pendente" e envia uma mensagem para uma fila de processamento.
4.  Um **Worker de Processamento** pega a mensagem da fila, baixa o documento do Cloud Storage e executa o pipeline de análise (OCR, extração, etc.).
5.  O Worker chama os **Serviços de IA Externos** (Gemini) para o enriquecimento semântico.
6.  O Worker atualiza a entrada do documento no PostgreSQL com os metadados gerados (resumo, tags) e o status "concluído".
7.  O Cliente, que pode estar monitorando o status do documento via polling ou WebSocket, é notificado e atualiza a UI para exibir os resultados para o usuário.
