# Documentação da API de Plugins (v1) - CartaOS

## 1. Visão Geral e Filosofia

Bem-vindo à API de Plugins do CartaOS! Nossa visão é capacitar desenvolvedores para construir novas e empolgantes funcionalidades sobre a plataforma CartaOS. A API foi projetada com segurança, simplicidade e poder em mente, permitindo que você acesse os dados do usuário de forma consentida e estenda a interface do usuário de maneira coesa.

*   **Segurança em Primeiro Lugar:** Os plugins operam em um ambiente de sandbox. Eles não têm acesso direto ao sistema de arquivos ou a dados arbitrários. Todo o acesso a dados é mediado pela API e requer o consentimento explícito do usuário.
*   **Foco na Experiência do Usuário:** A API permite que você adicione elementos de UI em pontos pré-definidos ("UI Hooks"), garantindo que a experiência do usuário permaneça consistente e intuitiva.

## 2. Primeiros Passos: Criando seu Primeiro Plugin

1.  **Registre-se como Desenvolvedor:** No seu perfil de usuário do CartaOS, haverá uma seção para se registrar como desenvolvedor. Isso lhe dará acesso a um painel para criar e gerenciar seus plugins.
2.  **Crie um Novo Plugin:** No painel de desenvolvedor, crie um novo plugin. Você receberá um `plugin_id` e um `client_secret` para autenticação.
3.  **Use o SDK:** Forneceremos um SDK oficial em Dart (para plugins que rodam no cliente) e bibliotecas para Go/Python (para plugins que possuem um backend próprio). O SDK simplificará a autenticação e a interação com a API.
4.  **Desenvolvimento Local:** O SDK permitirá que você rode seu plugin em um ambiente de desenvolvimento local, conectado a uma versão de desenvolvimento do CartaOS.

## 3. Autenticação (OAuth 2.0)

A interação do seu plugin com a API do CartaOS é protegida pelo padrão OAuth 2.0.

*   **Fluxo:** Quando um usuário instala seu plugin, ele será redirecionado para uma tela de consentimento do CartaOS. Nesta tela, serão listadas as permissões que seu plugin está solicitando (ex: "Ler metadados de documentos", "Adicionar notas aos documentos").
*   **Token de Acesso:** Se o usuário consentir, seu plugin receberá um `access_token` que deverá ser usado para fazer chamadas à API em nome daquele usuário. Estes tokens têm vida curta e devem ser renovados usando um `refresh_token`.
*   **O SDK cuidará da maior parte deste fluxo para você.**

## 4. Referência da API Core (RESTful)

*   **URL Base:** `https://api.cartaos.com/v1/`
*   **Autenticação:** `Authorization: Bearer <seu_access_token>`

### Endpoints de Documentos

#### `GET /documents`
*   **Descrição:** Retorna uma lista paginada dos metadados dos documentos do usuário.
*   **Permissão Necessária:** `documents:read`
*   **Resposta:**
    ```json
    {
      "documents": [
        {
          "documentId": "doc-uuid-1",
          "fileName": "Foucault_1975.pdf",
          "summary": "Este artigo discute...",
          "tags": ["poder", "disciplina"]
        }
      ]
    }
    ```

#### `GET /documents/{id}/full-text`
*   **Descrição:** Retorna o conteúdo de texto completo de um documento específico que já foi processado.
*   **Permissão Necessária:** `documents:read_content`
*   **Resposta:**
    ```json
    {
      "documentId": "doc-uuid-1",
      "content": "O texto completo do documento..."
    }
    ```

#### `POST /documents/{id}/metadata`
*   **Descrição:** Adiciona ou atualiza um campo de metadados customizado para um documento. Seu plugin poderá criar e gerenciar seus próprios metadados.
*   **Permissão Necessária:** `documents:write_metadata`
*   **Request Body:**
    ```json
    {
      "pluginId": "seu-plugin-id",
      "metadata": {
        "journalSuggestionScore": 0.85
      }
    }
    ```

## 5. UI Extension Points (Ganchos de UI)

Para que seu plugin pareça parte integrante do CartaOS, você poderá registrar componentes de UI em locais específicos. Isso será feito através de um arquivo de manifesto (`manifest.json`) no seu pacote de plugin.

**Exemplo de `manifest.json`:**

```json
{
  "pluginId": "my-journal-analyzer",
  "name": "Analisador de Periódicos",
  "uiHooks": [
    {
      "hookPoint": "DOCUMENT_VIEW_ACTION_BUTTON",
      "label": "Analisar Periódicos",
      "component": "./components/AnalyzeButton.js"
    },
    {
      "hookPoint": "DOCUMENT_VIEW_SIDEBAR_PANEL",
      "label": "Sugestões de Periódicos",
      "component": "./components/SuggestionsPanel.js"
    }
  ]
}
```

### Pontos de Hook Disponíveis (v1)

*   `DOCUMENT_VIEW_ACTION_BUTTON`
    *   **O que faz:** Adiciona um botão na barra de ações da tela de visualização de um documento.
    *   **Caso de Uso:** Disparar uma ação específica do seu plugin para o documento atual (ex: "Enviar para Análise de Plágio").

*   `DOCUMENT_VIEW_SIDEBAR_PANEL`
    *   **O que faz:** Adiciona um novo painel na barra lateral direita da tela de visualização de um documento.
    *   **Caso de Uso:** Exibir informações contextuais ou resultados da análise do seu plugin (ex: "Sugestões de Periódicos", "Análise de Sentimento").

*   `MAIN_NAV_ITEM`
    *   **O que faz:** Adiciona um novo item na barra de navegação principal da aplicação.
    *   **Caso de Uso:** Abrir uma tela inteira dedicada à funcionalidade principal do seu plugin (ex: um dashboard de análise de carreira).

## 6. Diretrizes e Boas Práticas

*   **Performance:** A UI do seu plugin deve ser leve e responsiva. Evite operações de bloqueio no thread principal.
*   **Privacidade:** Solicite apenas as permissões estritamente necessárias para o funcionamento do seu plugin. Seja transparente com o usuário sobre como os dados dele são utilizados.
*   **Design:** Siga o [Guia de Estilo de UI/UX](./17-Design-System-and-UI-UX-Style-Guide.md) do CartaOS para que seu plugin se integre visualmente à aplicação.
*   **Segurança:** Nunca peça ao usuário para inserir suas senhas ou chaves de API do CartaOS diretamente na interface do seu plugin.
