## Guia de Estilo do Projeto

Este documento descreve o estilo de codificação, as convenções de formatação e as melhores práticas para o projeto CartaOS. A adesão a este guia de estilo garante consistência, legibilidade e manutenibilidade em toda a base de código.

### 1. Princípios Gerais

*   **Legibilidade**: O código deve ser fácil de ler e entender por humanos.
*   **Consistência**: Mantenha um estilo consistente em todo o projeto.
*   **Clareza**: Evite construções inteligentes, mas obscuras. Prefira código claro e explícito.
*   **Simplicidade**: Mantenha o código o mais simples possível.
*   **DRY (Don't Repeat Yourself)**: Evite duplicar código.
*   **KISS (Keep It Simple, Stupid)**: Favoreça soluções diretas.

### 2. Idioma

*   **Idioma Padrão**: Use o inglês como idioma padrão para todo o código, incluindo comentários e documentação.
*   **Consistência**: Mantenha a consistência no idioma em todo o projeto.

### 3. Convenções de Nomenclatura

*   **Variáveis, Funções e Parâmetros**: `camelCase`. Nomes descritivos e significativos são preferidos.
    *   *Bom*: `userProfile`, `calculateTotalPrice`
    *   *Ruim*: `up`, `ctp`, `x`, `y`
*   **Classes, Enums, Typedefs e Extensões**: `PascalCase`.
    *   *Bom*: `UserProfile`, `OrderService`, `ProductType`
    *   *Ruim*: `user_profile`, `order_service`
*   **Constantes**: `UPPER_CASE_WITH_UNDERSCORES`.
    *   *Bom*: `MAX_RETRIES`, `DEFAULT_TIMEOUT`
    *   *Ruim*: `maxRetries`, `default_timeout`
*   **Arquivos**: `snake_case.dart`.
*   **Nomes de Branch**: `kebab-case` com um prefixo claro (e.g., `feature/add-user-auth`, `bugfix/fix-login-issue`, `chore/update-dependencies`).

### 4. Formatação

O formatador automático do Flutter (`flutter format`) deve ser usado sempre.

#### 4.1. Comprimento da Linha

*   **Comprimento Máximo da Linha**: 80 caracteres.

#### 4.2. Aspas

*   Prefira aspas simples (`'`) para strings.

### 5. Comentários

*   **Propósito**: Comentários devem explicar *por que* o código faz algo, não *o que* ele faz (a menos que o "o que" não seja imediatamente óbvio).
*   **Comentários de Documentação**: Use `///` para comentários de documentação para funções, classes e módulos para explicar seu propósito, argumentos e valores de retorno.
*   **Comentários TODO**: Use `// TODO:` para notas temporárias ou trabalho futuro.

### 6. Diretrizes Específicas do Dart/Flutter

*   Siga o [Guia de Estilo Efetivo do Dart](https://dart.dev/guides/language/effective-dart).
*   Use `flutter analyze` para linting.
*   Use `flutter format .` para formatação.
*   **Tipagem**: Use anotações de tipo explícitas.
*   **Async/Await**: Prefira `async/await` para operações assíncronas.

### 7. Controle de Versão (Git)

*   **Mensagens de Commit**: Siga a especificação de [Commits Convencionais](https://www.conventionalcommits.org/en/v1.0.0/).
    *   `tipo(escopo): descrição`
    *   Exemplo: `feat(auth): adiciona endpoint de registro de usuário`
*   **Estratégia de Branching**: Use um fluxo de trabalho de feature-branch.
*   **Pull Requests**: Forneça descrições claras, link para issues e garanta que todas as verificações passem antes do merge.

### 8. Revisão de Código

*   **Seja Construtivo**: Forneça feedback útil e acionável.
*   **Foque na Qualidade do Código**: Revise a correção, legibilidade, manutenibilidade e adesão ao guia de estilo.
*   **Aprove com Cuidado**: Garanta que o código atenda a todos os requisitos e padrões antes de aprovar.

Ao aderir a este guia de estilo, contribuímos coletivamente para uma base de código consistente, de alta qualidade e agradável de se trabalhar.