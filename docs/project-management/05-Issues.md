# Issues Iniciais do Projeto CartaOS

Este documento lista o conjunto inicial de issues para o projeto CartaOS, com base nas histórias de usuário e nos requisitos do MVP. Estas issues devem ser criadas no rastreador de issues do GitHub.

## Marco: Minimum Viable Product (MVP)

### Épico: Gerenciamento de Documentos

*   **Issue #1**: `feat(pipeline): Implementar a adição de arquivos PDF na caixa de entrada`
    *   **Descrição**: Implementar a funcionalidade de arrastar e soltar e de seleção de arquivos para adicionar PDFs à caixa de entrada.
    *   **História de Usuário**: HU-01
    *   **Labels**: `feature`, `component:frontend`, `priority:high`

*   **Issue #2**: `feat(pipeline): Implementar a triagem de tipo de PDF (digital vs. digitalizado)`
    *   **Descrição**: Desenvolver um módulo para analisar um PDF e determinar se ele contém texto nativo ou se é uma imagem escaneada.
    *   **História de Usuário**: HU-02
    *   **Labels**: `feature`, `component:pipeline`, `priority:high`

*   **Issue #3**: `feat(pipeline): Implementar a extração de texto de PDFs nativos`
    *   **Descrição**: Implementar a extração de texto de PDFs que já contêm uma camada de texto.
    *   **História de Usuário**: HU-03
    *   **Labels**: `feature`, `component:pipeline`, `priority:high`

*   **Issue #4**: `feat(pipeline): Integrar uma biblioteca de OCR para extração de texto de PDFs digitalizados`
    *   **Descrição**: Pesquisar, selecionar e integrar uma biblioteca de OCR para extrair texto de PDFs baseados em imagem.
    *   **História de Usuário**: HU-04
    *   **Labels**: `feature`, `component:pipeline`, `priority:medium`

*   **Issue #5**: `feat(ai): Integrar a API do Gemini para geração de resumos`
    *   **Descrição**: Implementar a chamada para a API do Gemini para gerar um resumo do texto extraído.
    *   **História de Usuário**: HU-05
    *   **Labels**: `feature`, `component:ai`, `priority:high`

*   **Issue #6**: `feat(ai): Integrar a API do Gemini para extração de conceitos-chave e tags`
    *   **Descrição**: Implementar a chamada para a API do Gemini para extrair conceitos-chave e tags do texto extraído.
    *   **História de Usuário**: HU-06
    *   **Labels**: `feature`, `component:ai`, `priority:high`

*   **Issue #7**: `feat(ui): Exibir o status de processamento do documento na UI`
    *   **Descrição**: Implementar a feedback visual na UI para mostrar o status de cada documento no pipeline de processamento.
    *   **História de Usuário**: HU-07
    *   **Labels**: `feature`, `component:ui/ux`, `priority:medium`

### Épico: Autenticação de Usuário

*   **Issue #8**: `feat(auth): Implementar a tela e o fluxo de registro de usuário`
    *   **Descrição**: Criar a UI e a lógica para que novos usuários possam se registrar com e-mail e senha.
    *   **História de Usuário**: HU-08
    *   **Labels**: `feature`, `component:auth`, `component:frontend`, `priority:high`

*   **Issue #9**: `feat(auth): Implementar a tela e o fluxo de login de usuário`
    *   **Descrição**: Criar a UI e a lógica para que usuários registrados possam fazer login.
    *   **História de Usuário**: HU-09
    *   **Labels**: `feature`, `component:auth`, `component:frontend`, `priority:high`

*   **Issue #10**: `feat(auth): Implementar a persistência da sessão de login`
    *   **Descrição**: Usar o `flutter_secure_storage` para armazenar e recuperar o token de autenticação, mantendo o usuário logado entre as sessões.
    *   **História de Usuário**: HU-10
    *   **Labels**: `feature`, `component:auth`, `priority:medium`

### Épico: Base de Conhecimento

*   **Issue #11**: `feat(ui): Implementar a visualização da lista de documentos processados`
    *   **Descrição**: Criar a UI para exibir a lista de documentos que foram processados com sucesso.
    *   **História de Usuário**: HU-11
    *   **Labels**: `feature`, `component:ui/ux`, `priority:high`

*   **Issue #12**: `feat(ui): Implementar a visualização detalhada do documento`
    *   **Descrição**: Criar a UI para exibir o resumo, os conceitos-chave e as tags de um documento selecionado.
    *   **História de Usuário**: HU-12
    *   **Labels**: `feature`, `component:ui/ux`, `priority:high`

*   **Issue #13**: `feat(export): Implementar a funcionalidade de exportação de documentos`
    *   **Descrição**: Implementar a lógica para exportar o PDF original e um arquivo Markdown com os metadados gerados.
    *   **História de Usuário**: HU-13
    *   **Labels**: `feature`, `component:frontend`, `priority:medium`
