# Roadmap de Produto - CartaOS

## 1. Filosofia do Roadmap

Este roadmap é um documento vivo, projetado para guiar o desenvolvimento do CartaOS de forma iterativa e incremental. Ele equilibra a visão de longo prazo com a necessidade de entregar valor contínuo aos nossos usuários. As fases não são estritamente sequenciais em todos os seus itens; o desenvolvimento de funcionalidades de uma fase posterior pode começar enquanto a fase atual está sendo finalizada.

--- 

## Fase 1: Fundação e Validação do Core (Duração: 3-6 meses)

*   **Tema/Meta:** Lançar um produto funcional (MVP) que valide a proposta de valor central: automação do fluxo de trabalho de documentos para pesquisadores. O foco é na estabilidade, na experiência do usuário do pipeline principal e na coleta de feedback inicial.

*   **Funcionalidades Chave:**
    *   `[MVP]` Aplicação Desktop Multiplataforma (Windows, macOS, Linux) com Flutter.
    *   `[MVP]` Sistema de Autenticação de Usuários (base para futuros planos).
    *   `[MVP]` Pipeline de Processamento Local: Adicionar PDF -> Triagem -> OCR/Extração -> Enriquecimento com IA (Resumo, Tags, Conceitos).
    *   `[MVP]` Base de Conhecimento com armazenamento local.
    *   `[MVP]` Funcionalidade de Exportação para formatos compatíveis com Obsidian/Logseq.

*   **Objetivo de Negócio:**
    *   Construir uma base inicial de usuários (early adopters) através de um programa beta.
    *   Validar a demanda pelo produto e a disposição dos usuários em adotar a ferramenta.
    *   Coletar dados e feedback para refinar as prioridades das próximas fases.

--- 

## Fase 2: O Pesquisador Conectado (Duração: 6-12 meses após a Fase 1)

*   **Tema/Meta:** Transformar o CartaOS de uma ferramenta local para uma plataforma conectada e mais inteligente, introduzindo a primeira camada de monetização.

*   **Funcionalidades Chave:**
    *   **Chat com Documentos (RAG):** Implementar a busca semântica e uma interface de chat para que os usuários possam "conversar" com sua base de conhecimento.
    *   **Sincronização na Nuvem:** Introduzir o armazenamento seguro de documentos e metadados na nuvem, permitindo o acesso a partir de múltiplos dispositivos.
    *   **Lançamento da Versão Web:** Disponibilizar as funcionalidades centrais em uma aplicação web acessível por qualquer navegador.
    *   **Integração com Zotero:** Implementar a sincronização bidirecional de metadados e PDFs com a biblioteca Zotero do usuário.

*   **Objetivo de Negócio:**
    *   Lançar o **Plano "Researcher" (Pago)**, oferecendo as funcionalidades avançadas (RAG, Sincronização na Nuvem) como um upgrade.
    *   Aumentar a retenção de usuários, tornando o CartaOS o centro do seu ecossistema de pesquisa.
    *   Expandir a base de usuários através da acessibilidade da versão web.

--- 

## Fase 3: O Assistente de Carreira e Ecossistema (Duração: 12-18 meses após a Fase 2)

*   **Tema/Meta:** Expandir o CartaOS para além da gestão de documentos, tornando-o um assistente proativo para a carreira acadêmica e abrindo a plataforma para desenvolvedores externos.

*   **Funcionalidades Chave:**
    *   **API de Plugins e Marketplace:** Lançar a primeira versão da API de plugins e uma loja onde desenvolvedores podem listar e vender suas criações.
    *   **Primeiros Plugins Premium:** Desenvolver e lançar os primeiros plugins proprietários focados em carreira:
        *   *Analisador de Periódicos:* Sugere os melhores periódicos para publicação com base no manuscrito.
        *   *Mapeamento de Fomento:* Busca e alerta sobre editais de financiamento relevantes.
    *   **Lançamento da Versão Mobile (iOS/Android):** Criar um aplicativo mobile focado em leitura, anotação de PDFs e captura rápida de novas ideias e referências.
    *   **Funcionalidades Colaborativas (V1):** Introduzir o compartilhamento de bibliotecas entre usuários para o plano de equipe.

*   **Objetivo de Negócio:**
    *   Criar novas fontes de receita através do marketplace de plugins (modelo de revenue share).
    *   Lançar o **Plano "Lab"**, focado em equipes e laboratórios de pesquisa.
    *   Aumentar o "efeito de rede" e a defesa da plataforma, tornando-a uma ferramenta indispensável para grupos.

--- 

## Fase 4: A Plataforma Acadêmica Completa (Duração: Contínua)

*   **Tema/Meta:** Consolidar o CartaOS como a plataforma definitiva para todo o ciclo de vida da pesquisa, integrando escrita, publicação e bem-estar.

*   **Funcionalidades Chave:**
    *   **Módulo de Escrita Integrado:** Um editor de texto (Markdown) com autocompletar de citações, assistente de escrita contextual (RAG) e integração com Pandoc para exportação.
    *   **Controle de Versão:** Utilizar Git nos bastidores para versionar automaticamente cada documento e suas análises.
    *   **Plataforma Inteligente de Peer Review:** Desenvolver um módulo para periódicos e conferências que utiliza IA para sugerir revisores e realizar pré-análises de submissões.
    *   **Módulo de Bem-Estar:** Integrar com calendários e monitorar padrões de trabalho para fornecer insights e alertas sobre risco de burnout.

*   **Objetivo de Negócio:**
    *   Expandir o modelo de negócios para o mercado B2B, vendendo a plataforma de Peer Review para editoras e universidades.
    *   Posicionar o CartaOS como um líder de pensamento em inovação na comunicação científica e bem-estar acadêmico.
    *   Alcançar a sustentabilidade de longo prazo através de múltiplas e diversificadas fontes de receita.
