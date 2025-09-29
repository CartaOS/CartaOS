# Especificação da API Interna (v1) - CartaOS

## 1. Introdução

Esta especificação descreve a API RESTful interna que servirá como a ponte de comunicação entre os clientes multiplataforma (Flutter) e o servidor backend do CartaOS. A API é projetada para ser segura, previsível e organizada por recursos.

*   **URL Base:** `https://api.cartaos.com/v1`
*   **Porta do Servidor:** `8080` (para desenvolvimento local)
*   **Formato de Dados:** Todas as requisições e respostas utilizarão o formato `application/json`.
*   **Autenticação:** Todas as rotas, exceto `/auth/*`, exigem um `Bearer Token` de autenticação no cabeçalho `Authorization`. O token é um JWT (JSON Web Token) obtido através do serviço de autenticação.

## 2. Autenticação

Gerencia o registro, login e renovação de tokens dos usuários.

### `POST /auth/register`
*   **Descrição:** Registra um novo usuário no sistema.
*   **Request Body:**
    ```json
    {
      "email": "user@example.com",
      "password": "strongpassword123",
      "fullName": "Ana da Silva"
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
      "userId": "uuid-goes-here",
      "email": "user@example.com",
      "fullName": "Ana da Silva"
    }
    ```

### `POST /auth/login`
*   **Descrição:** Autentica um usuário e retorna um token de acesso e um de atualização.
*   **Request Body:**
    ```json
    {
      "email": "user@example.com",
      "password": "strongpassword123"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "accessToken": "jwt_access_token_string",
      "refreshToken": "jwt_refresh_token_string"
    }
    ```

## 3. Usuários

Gerencia as informações do perfil do usuário autenticado.

### `GET /users/me`
*   **Descrição:** Retorna os detalhes do perfil do usuário atualmente autenticado, incluindo seu plano de assinatura.
*   **Success Response (200 OK):**
    ```json
    {
      "userId": "uuid-goes-here",
      "email": "user@example.com",
      "fullName": "Ana da Silva",
      "subscription": {
        "name": "Researcher",
        "allowCloudSync": true
      }
    }
    ```

## 4. Documentos

Gerencia o ciclo de vida dos documentos dos usuários.

### `POST /documents/initiate-upload`
*   **Descrição:** Inicia o processo de upload de um novo arquivo. O backend gera uma URL de upload segura e de curta duração para o cliente usar.
*   **Request Body:**
    ```json
    {
      "fileName": "Foucault_1975.pdf",
      "fileSizeBytes": 1234567,
      "mimeType": "application/pdf"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "documentId": "new-document-uuid",
      "uploadUrl": "https://storage.googleapis.com/signed-url-for-upload"
    }
    ```

### `GET /documents`
*   **Descrição:** Lista todos os documentos (e seus metadados) do usuário autenticado, com suporte a paginação.
*   **Query Parameters:** `?page=1&pageSize=20`
*   **Success Response (200 OK):**
    ```json
    {
      "documents": [
        {
          "documentId": "doc-uuid-1",
          "fileName": "Foucault_1975.pdf",
          "status": "completed",
          "createdAt": "2025-09-28T10:00:00Z",
          "summary": "Este artigo discute..."
        }
      ],
      "pageInfo": {
        "currentPage": 1,
        "totalPages": 5
      }
    }
    ```

### `POST /documents/{id}/start-processing`
*   **Descrição:** Notifica o backend que o upload do arquivo foi concluído (usando a `documentId` obtida em `initiate-upload`) e dispara o pipeline de processamento assíncrono na nuvem.
*   **Success Response (202 Accepted):**
    ```json
    {
      "message": "Document processing started."
    }
    ```

## 5. Chat Acadêmico (RAG)

Permite a interação em linguagem natural com a base de conhecimento do usuário.

### `POST /chat`
*   **Descrição:** Envia uma pergunta para a base de conhecimento do usuário e retorna uma resposta sintetizada com as fontes.
*   **Request Body:**
    ```json
    {
      "query": "Quais autores criticam a metodologia de Foucault?"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "response": "De acordo com Silva (2021), a principal crítica é a falta de rigor empírico [1].",
      "sources": [
        {
          "sourceId": 1,
          "documentId": "doc-uuid-of-silva-2021",
          "chunkText": "O trecho exato do documento de Silva..."
        }
      ]
    }
    ```

## 6. Marketplace de Plugins

Gerencia a descoberta e aquisição de plugins.

### `GET /plugins`
*   **Descrição:** Lista todos os plugins públicos disponíveis no marketplace, com filtros por categoria.
*   **Query Parameters:** `?category=writing`
*   **Success Response (200 OK):**
    ```json
    {
      "plugins": [
        {
          "pluginId": "plugin-uuid-123",
          "name": "Analisador de Periódicos",
          "developerName": "CartaOS Core",
          "price": 15.00,
          "shortDescription": "Sugere os melhores periódicos para seu artigo."
        }
      ]
    }
    ```

### `POST /plugins/{id}/purchase`
*   **Descrição:** Inicia o processo de compra de um plugin. A lógica de pagamento real seria integrada com um provedor como Stripe.
*   **Success Response (200 OK):**
    ```json
    {
      "userPluginId": "user-plugin-assoc-uuid",
      "status": "purchase_successful"
    }
    ```
