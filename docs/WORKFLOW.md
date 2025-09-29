# Fluxo de Trabalho de Desenvolvimento Completo para o CartaOS

Este documento fornece um fluxo de trabalho de desenvolvimento abrangente para o projeto CartaOS, incorporando as melhores práticas.

## 1. Configuração do Repositório

1.  Fork o repositório no GitHub
2.  Clone o seu repositório forkado localmente:
    ```bash
    git clone https://github.com/SEU_USUARIO/CartaOS.git
    ```
3.  Navegue até o diretório do projeto:
    ```bash
    cd CartaOS
    ```
4.  Adicione o repositório upstream:
    ```bash
    git remote add upstream https://github.com/lfgranja/CartaOS.git
    ```
5.  Verifique os remotes:
    ```bash
    git remote -v
    ```

## 2. Seleção de Issues e Branching

### Seleção de Issues

1.  Revise as issues abertas no GitHub, priorizando:
    *   Issues com a label `bug`
    *   Issues com a label `priority:high`
    *   Issues no marco atual
2.  Para novas funcionalidades, crie uma issue primeiro para discutir a proposta
3.  Comente na issue para indicar que você está trabalhando nela
4.  Atribua a issue a si mesmo, se possível

### Estratégia de Branching

1.  Sincronize com o upstream:
    ```bash
    git fetch upstream
    git checkout main
    git merge upstream/main
    ```
2.  Crie uma nova branch para sua issue:
    ```bash
    git switch -c feature/issue-NUMERO-breve-descricao main
    ```
    *   Substitua `NUMERO` pelo número real da issue
    *   Use nomes de branch descritivos em `kebab-case`
    *   Sempre faça a branch a partir da `main`

## 3. Processo de Desenvolvimento

1.  Siga o guia de estilo do projeto para os padrões de codificação
2.  Escreva testes para novas funcionalidades
3.  Execute os testes existentes para garantir que nada foi quebrado
4.  Siga o TDD (Test-Driven Development) sempre que aplicável
5.  Commite frequentemente com mensagens descritivas seguindo os Commits Convencionais

## 4. Qualidade e Testes de Código

1.  Execute as ferramentas de linting:
    *   `flutter analyze`
2.  Execute as ferramentas de formatação:
    *   `flutter format .`
3.  Execute os testes:
    *   `flutter test`

## 5. Diretrizes de Commit

1.  Crie uma mensagem de Commit Convencional:
    ```bash
    tipo(escopo): descrição

    [corpo opcional]

    [rodapé opcional]
    ```
2.  Use os tipos de commit apropriados:
    *   `feat`: Nova funcionalidade
    *   `fix`: Correção de bug
    *   `docs`: Alterações na documentação
    *   `style`: Alterações no estilo do código (formatação, etc.)
    *   `refactor`: Refatoração de código
    *   `perf`: Melhorias de performance
    *   `test`: Adicionando ou modificando testes
    *   `build`: Alterações no sistema de build
    *   `ci`: Alterações na configuração do CI
    *   `chore`: Tarefas de manutenção
    *   `revert`: Revertendo um commit anterior
3.  Mantenha as descrições concisas, no imperativo, com a primeira letra minúscula e sem ponto final
4.  Referencie as issues no rodapé:
    ```bash
    Fixes #123
    Closes #456
    ```

## 6. Checklist Pré-Push

1.  Faça o stage apenas das alterações relacionadas à issue atual
2.  Revise as alterações em stage:
    ```bash
    git diff --staged
    ```
3.  Execute todas as verificações de qualidade (linting, formatação, testes)
4.  Crie um commit final com uma mensagem de Commit Convencional
5.  Envie para o seu fork:
    ```bash
    git push origin feature/issue-NUMERO-breve-descricao
    ```

## 7. Processo de Pull Request

1.  Crie um pull request da sua branch para a branch `main` do repositório upstream
2.  Use o template de PR, se disponível
3.  Forneça uma descrição clara das alterações
4.  Link para a issue relacionada
5.  Solicite a revisão dos mantenedores
6.  Enderece qualquer feedback recebido durante o processo de revisão

## 8. Processo Pós-Aprovação do PR

Siga estritamente o processo documentado em [POSTPR.md](POSTPR.md) após a aprovação de um PR.

## 9. Arquitetura do Projeto e Stack de Tecnologia

Consulte a documentação de arquitetura e tecnologia do CartaOS para obter detalhes sobre o design modular, a stack de tecnologia e as ferramentas de desenvolvimento.

## 10. Princípios Fundamentais de Desenvolvimento

1.  Sempre adira às convenções do projeto para estilo, estrutura e arquitetura
2.  Mantenha a compatibilidade com versões anteriores sempre que possível
3.  Escreva documentação clara e abrangente para novas funcionalidades
4.  Siga as melhores práticas de segurança
5.  Considere as implicações de performance das alterações
6.  Escreva testes para todas as novas funcionalidades
7.  Use nomes de variáveis e funções descritivos
8.  Mantenha as funções pequenas e focadas
9.  Evite a duplicação de código
10. Siga a Regra do Escoteiro: "Sempre deixe o código melhor do que você o encontrou"

## 11. Colaboração e Comunicação

1.  Participe das discussões nas issues do GitHub
2.  Seja respeitoso e construtivo em todas as interações
3.  Peça ajuda quando necessário
4.  Forneça feedback a outros contribuidores
5.  Siga o código de conduta do projeto
