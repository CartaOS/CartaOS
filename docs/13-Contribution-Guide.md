# Guia de Contribuição - CartaOS v2

## 1. Nossa Filosofia de Contribuição

Bem-vindo(a) à comunidade CartaOS! Agradecemos imensamente seu interesse em contribuir. Acreditamos que a colaboração aberta é a chave para construir um produto que realmente atenda às necessidades da comunidade acadêmica. Este guia tem como objetivo tornar o processo de contribuição claro, transparente e gratificante para todos.

Seja você um desenvolvedor, um designer, um pesquisador com ideias ou alguém que encontrou um bug, sua contribuição é valiosa. Pedimos que siga este guia e sempre interaja de forma respeitosa, de acordo com o nosso [Código de Conduta](link-para-o-code-of-conduct.md).

## 2. Tipos de Contribuição

Existem duas maneiras principais de contribuir para o ecossistema CartaOS:

1.  **Contribuições para o Core Open Source:** Melhorias no cliente Flutter, que é e sempre será de código aberto. Isso inclui correções de bugs, melhorias de UI/UX, otimizações de performance e desenvolvimento de novas integrações open source.

2.  **Desenvolvimento de Plugins para o Marketplace:** Criação de novas funcionalidades como plugins que podem ser gratuitos ou pagos. Esta é uma ótima maneira de construir sobre a plataforma CartaOS e até mesmo gerar receita.

## 3. Contribuindo para o Core Open Source (Cliente Flutter)

### 3.1. Encontrando uma Tarefa

*   A melhor maneira de começar é visitando a nossa [página de Issues no GitHub](link-para-as-issues).
*   Procure por issues com as labels `good first issue` ou `help wanted`.
*   Se você tem uma nova ideia ou encontrou um bug, por favor, **crie uma nova issue** para discutir antes de começar a trabalhar. Isso garante que a sua contribuição esteja alinhada com o roadmap do projeto.
*   Quando decidir trabalhar em uma issue, deixe um comentário para que possamos atribuí-la a você.

### 3.2. Configurando o Ambiente de Desenvolvimento

1.  **Faça um Fork** do repositório principal para a sua conta no GitHub.
2.  **Clone** o seu fork localmente: `git clone https://github.com/SEU_USUARIO/CartaOS.git`
3.  **Adicione o repositório original** como `upstream`: `git remote add upstream https://github.com/CartaOS/CartaOS.git`
4.  **Instale as dependências** do Flutter seguindo as instruções no `README.md` principal.
5.  **Conecte-se ao Backend de Desenvolvimento:** Para contribuições no cliente, você não precisa rodar o backend localmente. A aplicação Flutter virá pré-configurada para se conectar a um ambiente de desenvolvimento público do nosso backend.

### 3.3. O Fluxo de Desenvolvimento

1.  **Sincronize seu branch `main`** com o `upstream`: `git checkout main && git pull upstream main`.
2.  **Crie um novo branch** para a sua feature ou correção: `git checkout -b feat/nome-da-feature` ou `fix/descricao-do-bug`.
3.  **Desenvolva e Teste:** Escreva seu código e, crucialmente, escreva os testes correspondentes (testes de unidade e de widget). Siga a nossa [Estratégia de Qualidade](./12-Testing-and-Quality-Strategy.md).
4.  **Verifique a Qualidade:** Antes de commitar, rode os verificadores locais: `flutter analyze` e `flutter format`.
5.  **Faça o Commit:** Use o padrão de [Conventional Commits](https://www.conventionalcommits.org). Ex: `feat(profile): add avatar upload functionality` ou `fix(chat): correct message ordering bug`.
6.  **Envie para o seu Fork:** `git push origin feat/nome-da-feature`.
7.  **Abra um Pull Request (PR):** No GitHub, abra um PR do seu branch para o branch `main` do repositório `upstream`. Preencha o template do PR, explicando o que você fez e por quê.

## 4. Desenvolvendo Plugins para o Marketplace

O desenvolvimento de plugins é um caminho fantástico para estender as funcionalidades do CartaOS.

### 4.1. Primeiros Passos

1.  **Leia a Documentação da API de Plugins:** O documento [Plugin API Documentation](./15-Plugin-API-Documentation.md) é a sua fonte da verdade. Ele explica como autenticar, como acessar os dados do usuário de forma segura e como registrar novos componentes na UI.
2.  **Obtenha uma Chave de Desenvolvedor:** Através do seu perfil no CartaOS, você poderá registrar-se como desenvolvedor e obter as credenciais necessárias para começar.
3.  **Use o SDK:** Forneceremos um SDK em Dart que facilitará a interação com a API do CartaOS, além de um repositório com exemplos de plugins.

### 4.2. Modelo de Negócios e Submissão

*   **Monetização:** Você pode optar por oferecer seu plugin gratuitamente ou como um produto pago.
*   **Compartilhamento de Receita:** Para plugins pagos, o CartaOS reterá uma porcentagem padrão da indústria (ex: 30%) para cobrir os custos de manutenção do marketplace, processamento de pagamentos e revisão. Os 70% restantes são seus.
*   **Processo de Revisão:** Todo plugin (gratuito ou pago) passará por um processo de revisão para garantir que ele atenda às nossas diretrizes de qualidade, segurança e privacidade antes de ser publicado no marketplace.
*   **Submissão:** O processo de submissão será feito através de um portal de desenvolvedores dentro do próprio CartaOS.

## 5. Padrões de Código

*   **Flutter/Dart:** Siga o [Guia de Estilo Oficial do Dart](https://dart.dev/guides/language/effective-dart/style) e as convenções da comunidade Flutter. Usamos `flutter analyze` para garantir a conformidade.
*   **Formatação:** A formatação é automatizada via `flutter format`. Execute-o antes de commitar.
*   **Arquitetura:** Siga os padrões de arquitetura (ex: gerenciamento de estado com Riverpod/BLoC) já estabelecidos no restante da aplicação para manter a consistência.
