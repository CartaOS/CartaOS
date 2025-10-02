# MVP e Requisitos do Produto - CartaOS

## 1. Objetivo do MVP

O Minimum Viable Product (MVP) tem como objetivo principal validar a hipótese central do CartaOS: **é possível agregar valor significativo ao fluxo de trabalho de um pesquisador automatizando o processamento e o enriquecimento semântico de documentos em uma única aplicação desktop.**

O foco é testar o pipeline de ponta a ponta com usuários reais, coletar feedback sobre a usabilidade e a utilidade das funcionalidades de IA, e estabelecer a base técnica para futuras expansões (web, mobile, colaboração).

## 2. Requisitos Funcionais do MVP

### RF-01: Autenticação de Usuário
*   **Descrição:** O sistema deve permitir que os usuários criem uma conta com e-mail e senha e façam login na aplicação desktop.
*   **Critérios de Aceite:**
    *   Um novo usuário pode se registrar com sucesso.
    *   Um usuário registrado pode fazer login.
    *   O estado de login é persistido entre as sessões do aplicativo.
    *   Este sistema servirá de base para a futura gestão de licenças e assinaturas.

### RF-02: Caixa de Entrada Unificada (Local)
*   **Descrição:** A interface principal deve apresentar uma área designada onde o usuário pode adicionar arquivos PDF do seu sistema de arquivos local.
*   **Critérios de Aceite:**
    *   O usuário pode arrastar e soltar um ou mais arquivos PDF na área designada.
    *   O usuário pode clicar em um botão para abrir um seletor de arquivos e escolher os PDFs.
    *   Os arquivos adicionados aparecem em uma lista de "pendentes" na UI.

### RF-03: Pipeline de Processamento Automatizado (Simplificado)
*   **Descrição:** Uma vez que um documento é adicionado, o sistema deve iniciar um pipeline de processamento em segundo plano.
*   **Critérios de Aceite:**
    *   **Triagem:** O sistema analisa o PDF e o classifica como "nascido digital" (contém texto) ou "digitalizado" (imagem).
    *   **Extração/OCR:** Se "nascido digital", o texto é extraído. Se "digitalizado", o sistema executa um processo de OCR para extrair o texto.
    *   **Enriquecimento Semântico:** O texto extraído é enviado para uma API de LLM (Gemini) para gerar um resumo conciso (aprox. 250 palavras), uma lista de 3-5 conceitos-chave e uma lista de 5-10 tags relevantes.
    *   O usuário pode ver o status de cada documento no pipeline (ex: "Processando...", "Concluído", "Erro").

### RF-04: Base de Conhecimento (Visualização Local)
*   **Descrição:** Após o processamento, os documentos e seus metadados gerados devem ser apresentados em uma interface de visualização.
*   **Critérios de Aceite:**
    *   Há uma seção na UI que lista todos os documentos concluídos.
    *   Ao selecionar um documento, a UI exibe:
        *   O nome do arquivo original.
        *   O resumo gerado pela IA.
        *   Os conceitos-chave e as tags em formato de lista ou badges.
    *   O sistema armazena localmente o PDF original e um arquivo Markdown (`.md`) associado contendo os metadados gerados em formato YAML Frontmatter.

### RF-05: Integração de Saída (Exportação)
*   **Descrição:** O usuário deve ser capaz de exportar os artefatos processados para uso em outras ferramentas.
*   **Critérios de Aceite:**
    *   Existe uma opção "Exportar" para cada documento concluído.
    *   A exportação cria uma pasta no local escolhido pelo usuário contendo o PDF original e o arquivo `.md` com os metadados.
    *   O formato do arquivo `.md` é compatível com ferramentas como Obsidian e Logseq.

## 3. Requisitos Não-Funcionais do MVP

### RNF-01: Plataforma
*   O MVP será uma aplicação desktop compatível com **Windows 10/11, macOS (Apple Silicon e Intel) e Linux (Debian/Ubuntu)**, construída com Flutter.

### RNF-02: Performance
*   A aplicação deve iniciar em menos de 5 segundos em hardware moderno.
*   A interface do usuário deve permanecer responsiva (sem travamentos) enquanto um documento está sendo processado em segundo plano.
*   O processamento de um documento de 20 páginas deve ser concluído em um tempo razoável (a ser definido, ex: < 2 minutos).

### RNF-03: Segurança
*   As senhas dos usuários devem ser armazenadas no banco de dados usando hashing forte (ex: bcrypt).
*   As chaves de API do LLM do usuário (se aplicável no modelo inicial) devem ser armazenadas de forma segura no cliente usando os mecanismos do sistema operacional (ex: Keychain no macOS, Credential Manager no Windows) através do pacote `flutter_secure_storage`.

### RNF-04: Usabilidade
*   A interface deve ser intuitiva, exigindo o mínimo de documentação para que um novo usuário entenda o fluxo de trabalho principal.
*   O sistema deve fornecer feedback claro sobre o status do processamento e quaisquer erros que ocorram.

## 4. Fora do Escopo para o MVP

As seguintes funcionalidades são intencionalmente deixadas de fora do MVP para garantir o foco e a velocidade de entrega:

*   **NÃO HAVERÁ** sincronização na nuvem ou armazenamento de documentos no backend.
*   **NÃO HAVERÁ** funcionalidades colaborativas.
*   **NÃO HAVERÁ** Chat com Documentos (RAG).
*   **NÃO HAVERÁ** integração direta com Zotero ou outras ferramentas (apenas exportação manual).
*   **NÃO HAVERÁ** aplicativos Web ou Mobile.
*   **NÃO HAVERÁ** marketplace de plugins.
*   **NÃO HAVERÁ** funcionalidades avançadas de edição de OCR ou limpeza de imagem (Laboratório de Restauração).
