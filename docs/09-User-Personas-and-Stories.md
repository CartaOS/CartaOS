# User Personas e User Stories - CartaOS v2

## 1. Introdução

Para garantir que estamos construindo um produto centrado no ser humano, definimos duas personas principais que representam os nossos segmentos de usuários mais importantes. Estas personas guiarão as nossas decisões de design, funcionalidades e priorização. Elas não são apenas demografias, mas representações de usuários reais com objetivos, dores e motivações.

--- 

## Persona 1: Ana, a Doutoranda Sobrecarrada

*   **Foto/Arquétipo:** Uma jovem de 28 anos, sentada em frente a um laptop, rodeada por pilhas de livros e artigos impressos. A expressão dela é uma mistura de determinação e cansaço.

*   **Background:**
    *   Ana está no segundo ano do seu doutorado em Ciências Sociais em uma universidade pública.
    *   Ela é apaixonada pelo seu tema de pesquisa, mas se sente constantemente afogada no volume de leitura necessário para definir seu referencial teórico e estado da arte.
    *   Ela tem habilidades digitais intermediárias, usando Zotero de forma básica e escrevendo seus trabalhos no Google Docs.

*   **Metas e Objetivos:**
    *   **Principal:** Concluir sua tese com uma contribuição original e de alta qualidade.
    *   **Secundário:** Publicar pelo menos um artigo em um periódico qualificado antes de defender a tese.
    *   **Imediato:** Superar o bloqueio da página em branco e começar a escrever sua revisão de literatura.

*   **Dores e Frustrações (Pains):**
    *   **"Estou me afogando em PDFs":** Ela baixa dezenas de artigos, mas eles ficam em uma pasta desorganizada. Ela não sabe por onde começar a ler.
    *   **Medo de Perder Algo Importante (FOMO):** "E se o artigo que muda toda a minha tese estiver em algum lugar que eu não procurei?"
    *   **Dificuldade de Síntese:** "Eu leio, leio, leio, mas tenho dificuldade em conectar as ideias de diferentes autores e identificar as verdadeiras lacunas no conhecimento."
    *   **Procrastinação na Escrita:** A tarefa de começar a escrever a revisão de literatura parece tão monumental que ela acaba adiando, focando em tarefas menores.

*   **User Stories (Histórias de Usuário):**

    *   **Epic: Organização e Triagem Inicial**
        *   "Como Ana, eu quero **arrastar uma pasta com 50 PDFs** para o CartaOS para que o sistema **processe todos em lote**, me dando uma visão geral rápida do material sem que eu precise abrir um por um."
        *   "Como Ana, eu quero que o sistema **extraia automaticamente os resumos e sugira tags** para cada artigo, para que eu possa **filtrar e priorizar** rapidamente quais ler primeiro."

    *   **Epic: Síntese e Descoberta de Conhecimento**
        *   "Como Ana, eu quero **fazer uma pergunta em linguagem natural**, como 'Quais autores criticam a teoria de Habermas?', para que eu possa **receber uma resposta sintetizada** com trechos dos meus documentos e links para as fontes, acelerando minha pesquisa."
        *   "Como Ana, eu quero **visualizar um mapa de como os conceitos se conectam** entre os artigos, para que eu possa **identificar os principais debates e autores** no meu campo."

    *   **Epic: Superando o Bloqueio da Escrita**
        *   "Como Ana, eu quero **selecionar 10 artigos relevantes e um tópico**, para que o CartaOS **gere um primeiro rascunho da minha revisão de literatura**, me ajudando a superar a inércia inicial."

--- 

## Persona 2: Dr. Carlos, o Líder de Laboratório Eficiente

*   **Foto/Arquétipo:** Um homem de 55 anos, em um escritório moderno, com uma lousa cheia de diagramas ao fundo. Ele está em uma videochamada, parecendo focado e um pouco apressado.

*   **Background:**
    *   Dr. Carlos é professor titular e líder de um laboratório de pesquisa em biotecnologia com 10 membros, incluindo pós-docs e doutorandos.
    *   Ele é um pesquisador experiente e respeitado, mas seu tempo é extremamente fragmentado entre pesquisa, orientação, aulas, administração e busca por financiamento.
    *   Ele é pragmático em relação à tecnologia: adota qualquer ferramenta que o ajude a economizar tempo e a aumentar a produtividade de sua equipe.

*   **Metas e Objetivos:**
    *   **Principal:** Garantir a sustentabilidade financeira e a reputação de seu laboratório através de publicações de alto impacto e financiamento contínuo.
    *   **Secundário:** Orientar seus alunos de forma eficaz para que se tornem pesquisadores independentes e bem-sucedidos.
    *   **Imediato:** Submeter dois artigos que estão em fase final de escrita e preparar uma nova proposta de financiamento para o próximo semestre.

*   **Dores e Frustrações (Pains):**
    *   **"Meu tempo é meu recurso mais escasso":** Ele não tem tempo para ler todos os artigos em profundidade e precisa confiar nos resumos de sua equipe.
    *   **"A burocracia é um dreno de energia":** Preencher relatórios e propostas de financiamento é uma tarefa que ele detesta e que o afasta da ciência.
    *   **Tomada de Decisão sob Incerteza:** "Escolher o periódico certo para submeter um artigo é uma aposta. Uma rejeição pode atrasar a publicação em meses."
    *   **Gestão de Equipe:** "É difícil acompanhar o progresso de múltiplos projetos e garantir que todos na equipe estejam alinhados e sendo produtivos."

*   **User Stories (Histórias de Usuário):**

    *   **Epic: Otimização da Publicação**
        *   "Como Dr. Carlos, eu quero **submeter o rascunho de um artigo** para que o CartaOS **analise o texto e me sugira 3 periódicos** com alta compatibilidade temática, fator de impacto relevante e histórico de publicação rápido."
        *   "Como Dr. Carlos, eu quero que o sistema **verifique automaticamente se o nosso manuscrito está em conformidade com as normas de formatação** do periódico alvo, para evitar rejeições técnicas."

    *   **Epic: Captação de Recursos**
        *   "Como Dr. Carlos, eu quero **colar o resumo de um novo projeto** para que o CartaOS **busque ativamente e me alerte sobre editais de fomento** nacionais e internacionais que se encaixem no escopo."

    *   **Epic: Gestão de Equipe e Colaboração**
        *   "Como Dr. Carlos, eu quero ter um **workspace compartilhado** onde eu possa ver todos os documentos e projetos do meu laboratório, para **facilitar a colaboração e o feedback** para minha equipe."
        *   "Como Dr. Carlos, eu quero um **dashboard que mostre o status de cada artigo em andamento** no meu laboratório (ex: 'Coleta de Dados', 'Escrita', 'Submetido'), para que eu possa **gerenciar o fluxo de trabalho da equipe** de forma eficaz."
