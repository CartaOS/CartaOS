# Plano de Testes e Estratégia de Qualidade - CartaOS v2

## 1. Filosofia de Qualidade

A qualidade no CartaOS não é uma etapa final, mas um princípio integrado em todo o ciclo de desenvolvimento. Nossa filosofia é que a qualidade é responsabilidade de toda a equipe. Adotamos uma abordagem de "shift-left", onde os testes e a garantia de qualidade são aplicados o mais cedo possível no processo para prevenir defeitos, em vez de apenas detectá-los.

## 2. A Pirâmide de Testes

Nossa estratégia de automação de testes seguirá o modelo da pirâmide de testes para garantir um feedback rápido, um custo de manutenção baixo e uma cobertura de risco eficaz.

```
      /\
     /  \
    / E2E \
   /-------\
  / Integração \
 /-------------\
/    Unidade    \
-----------------
```

### 2.1. Testes de Unidade (Base da Pirâmide)
*   **Objetivo:** Verificar se cada pequena unidade de código (função, método, classe) funciona como esperado, de forma isolada.
*   **Escopo:** A grande maioria dos nossos testes automatizados.
*   **Ferramentas:**
    *   **Backend (Go):** Pacote `testing` nativo do Go.
    *   **Frontend (Flutter):** Pacote `test` do Dart para lógica de negócios e `flutter_test` para testes de widgets individuais.
*   **Execução:** Executados automaticamente a cada salvamento de arquivo em ambiente de desenvolvimento e como um passo obrigatório no pipeline de CI antes de qualquer merge.

### 2.2. Testes de Integração (Meio da Pirâmide)
*   **Objetivo:** Verificar se diferentes partes do sistema funcionam corretamente juntas.
*   **Escopo:**
    *   **Integração de Serviços (Backend):** Testar se o serviço de API consegue se comunicar com o banco de dados, se o serviço de processamento consegue ler da fila de mensagens, etc. Usaremos um banco de dados de teste em um contêiner Docker.
    *   **Integração de Contrato (API):** Testar se as requisições e respostas entre o cliente Flutter e a API do backend aderem ao contrato definido na especificação da API.
    *   **Integração do Pipeline de IA:** Testar o fluxo completo de um documento, desde o upload até o enriquecimento, mockando as chamadas para as APIs externas (como Gemini) para garantir que nosso código de orquestração está correto.
*   **Ferramentas:**
    *   **Backend (Go):** `testing` com `testcontainers` para gerenciar dependências (ex: DB).
    *   **Frontend (Flutter):** `flutter_test` para testar fluxos que envolvem múltiplos widgets e serviços mockados.

### 2.3. Testes End-to-End (E2E) (Topo da Pirâmide)
*   **Objetivo:** Simular o fluxo de um usuário real através da aplicação completa para verificar se os cenários de negócios funcionam de ponta a ponta.
*   **Escopo:** Um número pequeno, mas crítico, de testes que cobrem os "happy paths" mais importantes.
    *   Exemplo de cenário: "Um usuário faz login, faz o upload de um PDF, aguarda o processamento, visualiza o resumo na base de conhecimento e faz uma pergunta sobre ele no chat."
*   **Ferramentas:**
    *   **Flutter:** Pacote `integration_test` com `flutter_driver` para automatizar a interação com a UI da aplicação rodando em um emulador ou dispositivo real.
*   **Execução:** Executados em um ambiente de staging antes de cada deploy para produção e em uma cadência regular (ex: todas as noites) contra o ambiente de produção para monitorar a saúde do sistema.

## 3. Estratégia de CI/CD (Integração e Deploy Contínuos)

*   **Ferramenta:** GitHub Actions.
*   **Gatilhos:** Cada `push` para um branch e cada `pull request` para o branch `main`.
*   **Pipeline de Pull Request (Obrigatório para Merge):**
    1.  **Lint & Format:** Verifica a conformidade do código com os guias de estilo.
    2.  **Testes de Unidade:** Executa todos os testes de unidade do frontend e do backend.
    3.  **Testes de Integração:** Executa os testes de integração em um ambiente containerizado.
    4.  **Análise de Código Estático:** Ferramentas como SonarCloud para detectar code smells, vulnerabilidades e bugs.
    5.  **Build:** Compila a aplicação para todas as plataformas alvo para garantir que não há erros de compilação.

*   **Pipeline de Deploy (Após Merge no `main`):**
    1.  Executa todos os passos do pipeline de PR.
    2.  Executa os testes E2E contra um ambiente de staging.
    3.  Se todos os testes passarem, o deploy para o ambiente de produção é feito de forma automática (ou manual, dependendo da política).

## 4. Testes Manuais e Qualidade

*   **Testes Exploratórios:** Antes de cada release majoritária, a equipe dedicará um tempo para realizar testes exploratórios, tentando "quebrar" a aplicação de formas que os testes automatizados não preveem.
*   **Programa de Beta:** Manter um canal de comunicação ativo com os usuários do programa de beta para receber feedback sobre usabilidade, bugs e sugestões de melhoria.
*   **Revisão de Código (Code Review):** Nenhum código será mesclado ao branch `main` sem a revisão e aprovação de pelo menos um outro membro da equipe. A revisão de código é uma ferramenta fundamental para garantir a qualidade, compartilhar conhecimento e manter a consistência do código.

## 5. Performance e Segurança

*   **Testes de Performance:** Integrar ferramentas de profiling (como o DevTools do Flutter) no processo de desenvolvimento para identificar gargalos de performance na UI. Testes de carga serão aplicados à API do backend antes de lançamentos importantes para garantir a escalabilidade.
*   **Testes de Segurança:** Realizar varreduras de segurança automatizadas no código e nas dependências (ex: `npm audit`, `gosec`). Testes de penetração serão contratados externamente antes do lançamento de funcionalidades financeiras críticas (como o marketplace).
