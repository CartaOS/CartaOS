# Design System & Guia de Estilo de UI/UX - CartaOS v2

## 1. Princípios Fundamentais de Design

A interface do CartaOS deve ser uma ferramenta que capacita, e não uma que distrai. Nosso design é guiado por três princípios fundamentais:

1.  **Clareza e Foco:** A interface deve ser limpa, organizada e livre de desordem. O objetivo é permitir que o pesquisador se concentre em seu conteúdo e em suas ideias, com a UI agindo como um pano de fundo discreto e funcional.

2.  **Intuitividade:** O fluxo de trabalho deve ser natural e previsível. Um novo usuário deve ser capaz de entender as funcionalidades principais sem a necessidade de um manual extenso. As ações devem ser lógicas e os resultados, esperados.

3.  **Calma e Sustentabilidade:** A pesquisa é uma maratona, não um sprint. O design deve promover um ambiente de trabalho calmo e sustentável. Evitaremos notificações excessivas, cores berrantes ou elementos que criem uma falsa sensação de urgência. O **Modo Escuro** será tratado como um requisito de primeira classe, não uma reflexão tardia, para reduzir o cansaço visual durante longas sessões de trabalho.

## 2. Paleta de Cores

A paleta de cores é minimalista e profissional, projetada para ser fácil de ler e não causar fadiga ocular.

### Modo Escuro (Padrão)
*   **Background Principal:** Um cinza muito escuro, quase preto (`#121212`). Evita o preto puro para reduzir o contraste excessivo.
*   **Background Secundário (Painéis, Cartões):** Um cinza ligeiramente mais claro (`#1E1E1E`).
*   **Texto Principal:** Branco com uma leve tonalidade de cinza (`#E0E0E0`).
*   **Texto Secundário (Metadados, placeholders):** Cinza médio (`#888888`).
*   **Cor de Destaque (Ações Primárias, Links, Foco):** Um azul calmo e acessível (`#4A90E2`).
*   **Sucesso:** Verde (`#34A853`).
*   **Erro:** Vermelho (`#EA4335`).
*   **Aviso:** Amarelo/Laranja (`#FBBC05`).

### Modo Claro
*   **Background Principal:** Branco (`#FFFFFF`).
*   **Background Secundário:** Cinza muito claro (`#F5F5F5`).
*   **Texto Principal:** Cinza escuro (`#202124`).
*   **Texto Secundário:** Cinza médio (`#5F6368`).
*   **Cor de Destaque:** O mesmo azul (`#4A90E2`).

## 3. Tipografia

A tipografia é escolhida para otimizar a legibilidade em longas sessões de leitura e para uma clareza nítida na interface.

*   **Fonte da Interface (UI):** **Inter**.
    *   **Justificativa:** Uma fonte sans-serif moderna, altamente legível em vários tamanhos e pesos. É neutra e profissional, ideal para botões, menus e outros elementos da UI.

*   **Fonte de Conteúdo (Leitura):** **Lora**.
    *   **Justificativa:** Uma fonte serifada contemporânea, com curvas suaves que a tornam extremamente confortável para a leitura de textos longos (como o conteúdo dos artigos e resumos). Cria uma distinção clara entre o "conteúdo" e o "chrome" da aplicação.

*   **Hierarquia de Texto:**
    *   Títulos de Página (H1): Inter Bold, 24px
    *   Títulos de Seção (H2): Inter Bold, 20px
    *   Texto do Corpo da UI: Inter Regular, 16px
    *   Texto de Conteúdo (Artigos): Lora Regular, 18px, com altura de linha de 1.6.

## 4. Iconografia

*   **Estilo:** Ícones de linha (line icons), minimalistas e consistentes.
*   **Biblioteca:** **Lucide Icons** (ou similar, como Feather Icons).
*   **Justificativa:** Oferece um conjunto abrangente e visualmente coeso de ícones que são claros, leves e não sobrecarregam a interface.

## 5. Componentes da Biblioteca de UI (Base)

Desenvolveremos uma biblioteca de componentes reutilizáveis no Flutter para garantir consistência em toda a aplicação.

*   **Botões:**
    *   **Primário:** Fundo sólido na cor de destaque (`#4A90E2`), texto branco.
    *   **Secundário:** Bordas na cor de destaque, fundo transparente, texto na cor de destaque.
    *   **Terciário (ou de Texto):** Sem bordas ou fundo, apenas o texto na cor de destaque.

*   **Campos de Texto (Inputs):**
    *   Bordas sutis, com a cor de destaque aparecendo na borda e no rótulo quando o campo está em foco.

*   **Cartões (Cards):**
    *   Usados para listar documentos, plugins, etc.
    *   Fundo na cor secundária, com uma sombra muito sutil para criar profundidade.
    *   Cantos arredondados (ex: 8px).

*   **Badges/Tags:**
    *   Pequenos elementos com cantos arredondados para exibir tags e conceitos-chave.
    *   Fundo em uma versão de baixa saturação da cor de destaque ou outras cores do sistema.

*   **Barras de Progresso:**
    *   Animações suaves para indicar o progresso. Cor de destaque para o preenchimento.

## 6. Espaçamento e Grid

*   **Sistema de Espaçamento:** Utilizar um sistema baseado em múltiplos de 8 (8px, 16px, 24px, 32px) para margens, paddings e espaçamento entre elementos. Isso cria um ritmo visual consistente e harmonioso.
*   **Grid:** O layout principal (ex: as três colunas da Base de Conhecimento) deve ser responsivo, adaptando-se a diferentes tamanhos de tela, desde um monitor ultrawide até a tela de um laptop.
