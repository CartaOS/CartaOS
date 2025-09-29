# Wireframes (Descrições Textuais) - CartaOS v2

## 1. Introdução

Estes wireframes textuais descrevem a estrutura, o layout e o fluxo de usuário para as telas principais da aplicação CartaOS. Eles servem como um guia para o desenvolvimento da UI no Flutter, focando na funcionalidade e na experiência do usuário antes da aplicação do design visual final.

--- 

## Tela 1: Dashboard Principal / Caixa de Entrada

*   **Objetivo:** Fornecer um ponto de entrada claro e simples para adicionar novos documentos e visualizar o status do trabalho em andamento.

*   **Layout:** Duas seções principais em uma única tela.

*   **Componentes Chave:**
    1.  **Barra de Navegação Lateral (Fixa à Esquerda):**
        *   Ícone do Logo do CartaOS no topo.
        *   Ícone e texto: "Caixa de Entrada" (Tela atual).
        *   Ícone e texto: "Base de Conhecimento".
        *   Ícone e texto: "Chat Acadêmico".
        *   Ícone e texto: "Marketplace de Plugins".
        *   Na parte inferior: Ícone do perfil do usuário (abre menu de configurações e logout) e um ícone de "Configurações".

    2.  **Área de Conteúdo Principal:**
        *   **Seção de Upload (Topo):**
            *   Uma grande área retangular com bordas pontilhadas.
            *   Texto central: "Arraste e solte seus arquivos PDF aqui".
            *   Abaixo do texto, um botão com o rótulo "Ou selecione arquivos do seu computador".
        *   **Seção de Fila de Processamento (Abaixo do Upload):**
            *   Título: "Fila de Processamento".
            *   Uma lista de itens, onde cada item representa um documento sendo processado.
            *   **Cada item da lista contém:**
                *   Ícone do tipo de arquivo (ex: ícone de PDF).
                *   Nome do arquivo (ex: `Foucault_VigiarEPunir_1975.pdf`).
                *   À direita, um indicador de status: `Processando...`, `Concluído`, `Erro`.
                *   Uma barra de progresso visual que avança conforme o pipeline é executado.

*   **Fluxo do Usuário:**
    1.  O usuário abre o aplicativo e aterrissa nesta tela.
    2.  Ele arrasta um PDF para a área de upload.
    3.  O arquivo aparece imediatamente na seção "Fila de Processamento" com o status "Processando...".
    4.  A barra de progresso é atualizada em tempo real.
    5.  Quando concluído, o status muda para "Concluído" e o item pode, opcionalmente, desaparecer da fila após alguns segundos ou ao navegar para outra tela.

--- 

## Tela 2: Base de Conhecimento

*   **Objetivo:** Permitir que o usuário explore, leia e gerencie todos os seus documentos processados.

*   **Layout:** Um layout de três colunas, clássico de aplicações de produtividade.

*   **Componentes Chave:**
    1.  **Coluna da Esquerda (Lista de Documentos):**
        *   Campo de busca no topo: "Buscar em seus documentos...".
        *   Abaixo da busca, botões de filtro: "Filtrar por Tags", "Filtrar por Autor".
        *   Uma lista rolável de todos os documentos processados.
        *   **Cada item da lista contém:**
            *   Título do documento (extraído ou nome do arquivo).
            *   Um trecho do resumo gerado pela IA.
            *   Badges coloridas para as principais tags.
            *   O item selecionado no momento fica destacado.

    2.  **Coluna Central (Visualizador de Conteúdo Enriquecido):**
        *   Exibe o conteúdo do arquivo `.md` associado ao documento selecionado na coluna da esquerda.
        *   **Topo:** Título do documento.
        *   **Seção de Metadados:** Um cabeçalho claro com o Resumo, os Conceitos-Chave e as Tags.
        *   **Corpo Principal:** O texto completo extraído do documento, formatado em Markdown para fácil leitura.
        *   **Botões de Ação no Topo:** "Exportar", "Adicionar à Citação", "Deletar".

    3.  **Coluna da Direita (Visualizador de PDF Original):**
        *   Renderiza o arquivo PDF original.
        *   Permite que o usuário role, dê zoom e navegue pelo documento.
        *   **Funcionalidade de Anotação (Pós-MVP):** Ferramentas para destacar texto e adicionar comentários. As anotações feitas aqui seriam automaticamente adicionadas ao arquivo `.md` na coluna central.

*   **Fluxo do Usuário:**
    1.  O usuário clica em "Base de Conhecimento" na barra de navegação.
    2.  Ele vê a lista de seus documentos na coluna da esquerda.
    3.  Ele clica em um documento. O conteúdo enriquecido aparece na coluna central e o PDF original na coluna da direita.
    4.  Ele pode ler o resumo rapidamente no centro ou consultar o original à direita.

--- 

## Tela 3: Chat Acadêmico (RAG)

*   **Objetivo:** Permitir que o usuário faça perguntas em linguagem natural sobre todo o seu acervo de documentos.

*   **Layout:** Interface de chat familiar.

*   **Componentes Chave:**
    1.  **Área de Conversa Principal:**
        *   Uma área rolável que exibe o histórico da conversa.
        *   **Mensagens do Usuário:** Alinhadas à direita.
        *   **Respostas do Assistente:** Alinhadas à esquerda.
        *   **Respostas com Fontes:** As respostas geradas pelo assistente que se baseiam em documentos específicos conterão notas de rodapé ou links clicáveis (ex: `[1]`, `[2]`).

    2.  **Rodapé da Tela:**
        *   Um campo de texto com o placeholder "Faça uma pergunta sobre seus documentos...".
        *   Um botão de "Enviar".

    3.  **Painel de Fontes (Opcional, pode ser um pop-up):**
        *   Ao clicar em um link de fonte na resposta (ex: `[1]`), um painel lateral ou um pop-up exibe o trecho exato do documento original de onde a informação foi extraída, com um link para abrir o documento completo na Base de Conhehecimento.

*   **Fluxo do Usuário:**
    1.  O usuário clica em "Chat Acadêmico".
    2.  Ele digita uma pergunta, como: "Quais são as principais críticas à metodologia de Foucault nos meus artigos?"
    3.  Ele pressiona "Enviar".
    4.  O assistente exibe uma mensagem de "Pensando..." e depois gera uma resposta sintetizada.
    5.  A resposta contém trechos como: "...de acordo com Silva (2021), a principal crítica é a falta de rigor empírico [1]. Já para Costa (2019), o problema reside na generalização excessiva [2]."
    6.  O usuário clica em `[1]` e vê o parágrafo exato do artigo de Silva (2021).

--- 

## Tela 4: Marketplace de Plugins

*   **Objetivo:** Criar um local central para os usuários descobrirem, comprarem e gerenciarem plugins que estendem a funcionalidade do CartaOS.

*   **Layout:** Uma grade de cartões, semelhante a uma loja de aplicativos.

*   **Componentes Chave:**
    1.  **Página Principal da Loja:**
        *   **Barra de Busca:** "Buscar plugins...".
        *   **Categorias:** Botões para filtrar por categorias como "Carreira", "Escrita", "Análise de Dados", "Produtividade".
        *   **Grade de Plugins:**
            *   Uma grade de cartões, onde cada cartão representa um plugin.
            *   **Cada cartão contém:** Ícone do plugin, Nome do plugin, Nome do desenvolvedor, Preço (ou "Gratuito"), e uma avaliação por estrelas.

    2.  **Página de Detalhes do Plugin:**
        *   Acessada ao clicar em um cartão.
        *   **Cabeçalho:** Ícone, Nome do Plugin, Desenvolvedor.
        *   **Botão de Ação Principal:** "Comprar por $XX,XX" ou "Instalar" (se gratuito).
        *   **Corpo:** Uma descrição detalhada do que o plugin faz, com screenshots ou GIFs.
        *   **Seção de Avaliações:** Lista de avaliações e comentários de outros usuários.

    3.  **Aba "Meus Plugins":**
        *   Uma aba na página do marketplace que lista todos os plugins que o usuário já instalou.
        *   Permite ao usuário ativar/desativar ou desinstalar um plugin.

*   **Fluxo do Usuário:**
    1.  O usuário clica em "Marketplace de Plugins".
    2.  Ele navega pelos plugins ou busca por "periódicos".
    3.  Ele encontra o plugin "Analisador de Periódicos" e clica nele.
    4.  Na página de detalhes, ele lê a descrição e decide comprar.
    5.  Após a compra, o botão muda para "Instalado" e uma nova funcionalidade aparece na UI do CartaOS (ex: um novo botão em um documento de rascunho).
