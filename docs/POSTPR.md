# Processo Pós-Aprovação de PR

Este documento descreve o processo abrangente a ser seguido após a aprovação e merge de um Pull Request (PR) na branch `main`. Este processo garante que todas as contribuições sejam devidamente integradas, documentadas e mantidas, aderindo aos padrões de qualidade do projeto.

### 1. Atualização da Documentação

Após o merge de um PR, é crucial atualizar toda a documentação relevante para refletir as alterações. Isso inclui:

*   **Documentação do Usuário**: Atualize os manuais do usuário, READMEs e quaisquer guias que os usuários possam consultar. Garanta que as novas funcionalidades sejam explicadas claramente e que quaisquer alterações na funcionalidade existente sejam anotadas.
*   **Documentação do Desenvolvedor**: Atualize a documentação da API, os documentos de design interno e quaisquer outros recursos que os desenvolvedores usam. Isso garante que futuros contribuidores entendam o novo código e suas implicações.
*   **`CHANGELOG.md`**: Adicione uma entrada ao arquivo `CHANGELOG.md`, resumindo as alterações introduzidas pelo PR. Siga a especificação de Commits Convencionais para a entrada do changelog.
*   **`CONTRIBUTING.md`**: Se o PR introduzir novas práticas ou ferramentas de desenvolvimento, atualize o `CONTRIBUTING.md` para refletir essas alterações.

### 2. Rastreamento e Fechamento de Issues

Gerencie adequadamente as issues associadas no GitHub:

*   **Feche a(s) Issue(s) Associada(s) ao PR**: Garanta que todas as issues diretamente abordadas pelo PR mergeado sejam fechadas. Use as palavras-chave apropriadas do GitHub (e.g., `Closes #NUMERO_DA_ISSUE`, `Fixes #NUMERO_DA_ISSUE`) na mensagem de commit do merge para automatizar isso.
*   **Crie Issues de Acompanhamento**: Se o PR introduzir novos itens de trabalho, limitações conhecidas ou áreas para melhoria futura, crie novas issues para eles. Atribua labels apropriadas (e.g., `enhancement`, `bug`, `technical debt`) e prioridades.
*   **Avalie as Contribuições dos Revisores**: **MUITO IMPORTANTE**: Como parte do processo de merge, avalie todas as contribuições (comentários, revisões, sugestões e melhorias) de `gemini-code-assist`, `qodo-merge-pro` ou quaisquer outros revisores. Para contribuições válidas, incorpore-as em novas issues ou consolide-as em issues existentes, garantindo a categorização, rotulagem e atribuição de prioridade adequadas. Isso garante que um feedback valioso não seja perdido e seja rastreado para ações futuras.

### 3. Garantia de Qualidade e Testes

Mesmo após o merge de um PR, a garantia de qualidade contínua é vital:

*   **Monitore os Pipelines de CI/CD**: Garanta que os pipelines de CI/CD continuem passando após o merge. Enderece quaisquer novas falhas imediatamente.
*   **Testes de Integração**: Se o PR envolveu alterações significativas, considere executar testes de integração adicionais na branch `main` para garantir a compatibilidade com outros componentes.
*   **Testes Manuais (se aplicável)**: Para funcionalidades críticas ou alterações na UI, realize testes manuais na branch `main` para verificar a funcionalidade e a experiência do usuário.

### 4. Planejamento de Release

Prepare-se para futuros releases:

*   **Branch de Feature**: Se o PR mergeado faz parte de uma feature maior, garanta que a branch `main` esteja estável e pronta para desenvolvimento futuro.
*   **Preparação das Notas de Release**: Comece a redigir as notas de release para o próximo release planejado, incorporando as alterações do PR mergeado.

### 5. Comunicação

Comunique as alterações às partes interessadas relevantes:

*   **Notificação da Equipe**: Informe a equipe de desenvolvimento sobre o PR mergeado e suas implicações.
*   **Atualizações da Comunidade**: Se a alteração for significativa e impactar os usuários, considere anunciá-la através dos canais apropriados da comunidade (e.g., fóruns do projeto, listas de e-mail, mídias sociais).

Ao seguir este processo abrangente de pós-aprovação de PR, garantimos que nosso projeto permaneça robusto, bem documentado e melhore continuamente a cada contribuição.
