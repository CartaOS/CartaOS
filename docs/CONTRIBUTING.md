## Contribuindo para o CartaOS

Agradecemos o seu interesse em contribuir para o CartaOS! Ao participar deste projeto, você concorda em seguir nosso [Código de Conduta](CODE_OF_CONDUCT.md).

### Como Posso Contribuir?

Existem muitas maneiras de contribuir, não apenas escrevendo código:

*   **Relatando Bugs**: Se você encontrar um bug, por favor, abra uma issue no GitHub.
*   **Sugerindo Funcionalidades**: Tem uma ideia para uma nova funcionalidade? Abra uma issue para discuti-la.
*   **Melhorando a Documentação**: Ajude-nos a tornar nossa documentação mais clara, precisa e abrangente.
*   **Escrevendo Código**: Corrija bugs, implemente novas funcionalidades ou refatore o código existente.
*   **Revisando Código**: Forneça feedback em pull requests de outros contribuidores.
*   **Respondendo a Perguntas**: Ajude outros usuários em issues ou discussões.

### Começando

1.  **Fork o Repositório**: Comece fazendo um fork do repositório do projeto para sua conta no GitHub.
2.  **Clone o Seu Fork**:
    ```bash
    git clone https://github.com/SEU_USUARIO/CartaOS.git
    cd CartaOS
    ```
3.  **Adicione o Repositório Upstream**:
    ```bash
    git remote add upstream https://github.com/lfgranja/CartaOS.git
    git fetch upstream
    ```
4.  **Crie uma Nova Branch**: Sempre crie uma nova branch para o seu trabalho. Faça a branch a partir da `main`.
    ```bash
    git checkout main
    git pull upstream main # Garanta que sua branch main esteja atualizada
    git switch -c feature/sua-feature # Para novas funcionalidades
    # ou
    git switch -c bugfix/issue-123-descricao # Para correções de bugs
    ```
    Por favor, use nomes de branch descritivos seguindo o `kebab-case`.

### Fluxo de Trabalho de Desenvolvimento

1.  **Sincronize com o Upstream**: Antes de iniciar um novo trabalho, sempre sincronize sua branch `main` com a branch `main` do upstream.
    ```bash
    git checkout main
    git pull upstream main
    ```
2.  **Faça Suas Alterações**:
    *   Siga o [Guia de Estilo](STYLEGUIDE.md) do projeto.
    *   Escreva testes para novas funcionalidades ou correções de bugs.
    *   Garanta que os testes existentes passem.
    *   Siga o [Desenvolvimento Guiado por Testes (TDD)](WORKFLOW.md#3-desenvolvimento) sempre que aplicável.
3.  **Execute as Verificações de Qualidade**: Antes de commitar, execute todas as verificações de qualidade locais.
    *   **Linting**: `flutter analyze`
    *   **Formatação**: `flutter format .`
    *   **Testes**: `flutter test`
4.  **Commite Suas Alterações**:
    *   Use [Commits Convencionais](https://www.conventionalcommits.org/en/v1.0.0/) para suas mensagens de commit.
    *   Exemplo: `feat(auth): adiciona endpoint de registro de usuário` ou `fix(parser): lida com entrada vazia de forma graciosa`
    *   Referencie issues relacionadas no corpo da mensagem de commit (e.g., `Fixes #123`).
5.  **Envie para o Seu Fork**:
    ```bash
    git push origin sua-branch
    ```

### Enviando um Pull Request (PR)

1.  **Abra um PR**: Vá para o seu repositório forkado no GitHub e abra um novo pull request da sua branch para a branch `main` do repositório *original*.
2.  **Preencha o Template**: Se um template de PR for fornecido, por favor, preencha-o completamente.
3.  **Descreva Suas Alterações**: Explique claramente o propósito do seu PR, quais alterações você fez e por quê.
4.  **Link para Issues**: Referencie quaisquer issues relacionadas (e.g., `Closes #123`, `Resolves #456`).
5.  **Solicite Revisão**: Solicite revisões dos mantenedores do projeto.
6.  **Enderece o Feedback**: Seja responsivo ao feedback durante o processo de revisão. Faça as alterações necessárias e envie novos commits para sua branch.

### Pós-Aprovação do PR

Após a aprovação e merge do seu PR, por favor, siga os passos descritos em [POSTPR.md](POSTPR.md). Isso inclui a atualização da documentação, o fechamento de issues e a avaliação das contribuições dos revisores.

### Código de Conduta

Por favor, revise nosso [Código de Conduta](CODE_OF_CONDUCT.md) para entender as expectativas de participação em nossa comunidade.

Obrigado por contribuir!
