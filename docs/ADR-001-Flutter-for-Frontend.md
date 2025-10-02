# ADR-001: Adoção do Flutter para o Frontend Multiplataforma

*   **Status:** Aceito
*   **Data:** 2025-09-28

## Contexto

A visão de produto para o CartaOS v2 exige uma presença em múltiplas plataformas: Desktop (Windows, macOS, Linux), Web e Mobile (iOS, Android). A manutenção de bases de código nativas separadas para cada uma dessas plataformas (ex: Swift/SwiftUI para iOS/macOS, Kotlin/Compose para Android, C#/.NET para Windows, e um framework web como React/Svelte) é logisticamente complexa e financeiramente inviável para uma equipe enxuta.

Isso criaria uma sobrecarga massiva de desenvolvimento, dificultaria a manutenção da paridade de funcionalidades entre as plataformas e aumentaria drasticamente o tempo de lançamento de novos recursos. Precisamos de uma solução que nos permita alcançar todas as plataformas alvo com uma única base de código, sem comprometer significativamente a performance ou a experiência do usuário.

## Decisão

Nós decidimos adotar o framework **Flutter**, utilizando a linguagem **Dart**, como a tecnologia principal para o desenvolvimento de toda a interface do cliente (frontend) do CartaOS v2.

## Justificativa

A escolha pelo Flutter é baseada em quatro pilares principais:

1.  **Base de Código Única e Verdadeira Multiplataforma:** Flutter permite o desenvolvimento e a compilação para todas as nossas seis plataformas alvo (Windows, macOS, Linux, Web, iOS, Android) a partir de um único repositório e código. Esta é a sua vantagem estratégica mais significativa, pois maximiza a eficiência do desenvolvimento.

2.  **Performance Nativa:** Diferente de soluções baseadas em web wrappers (como Electron), o Flutter não empacota um navegador. Ele compila o código Dart para código de máquina nativo (ARM, x86) e utiliza seu próprio motor de renderização de alta performance (Skia) para desenhar a UI diretamente na tela. Isso resulta em aplicações com inicialização rápida, animações fluidas a 60/120fps e uma sensação de responsividade nativa.

3.  **UI Consistente e Controlada:** Como o Flutter controla cada pixel na tela, ele garante que a interface do usuário, o design system e a experiência de uso sejam virtualmente idênticos em todas as plataformas. Isso fortalece a identidade da marca CartaOS e reduz o tempo gasto com ajustes de CSS ou layout específicos para cada plataforma.

4.  **Ecossistema Forte e Apoio do Google:** Flutter é um projeto de código aberto apoiado pelo Google, com uma comunidade grande, ativa e crescente. O repositório de pacotes `pub.dev` é vasto e maduro, oferecendo soluções prontas para a maioria dos desafios comuns (gerenciamento de estado, armazenamento seguro, comunicação de rede, etc.), o que acelera o desenvolvimento.

### Alternativas Consideradas

*   **Tauri/Svelte (Arquitetura Atual):** Embora excelente para aplicações desktop leves, a expansão para mobile exigiria uma reescrita completa em outro framework (como React Native ou nativo). A manutenção da paridade entre a versão web/desktop e a mobile seria um desafio.
*   **React Native:** Forte no mobile, mas o suporte para desktop ainda é menos maduro e mais fragmentado que o do Flutter. A performance, especialmente em aplicações complexas, pode não ser tão consistente quanto a do Flutter.
*   **Desenvolvimento Nativo Separado:** Rejeitado por ser inviável em termos de custo, tempo e tamanho da equipe.

## Consequências

*   **Positivas:**
    *   Redução drástica no tempo e custo de desenvolvimento e manutenção.
    *   Equipe de frontend unificada, focada em uma única stack (Dart/Flutter).
    *   Lançamento mais rápido de funcionalidades em todas as plataformas simultaneamente.
    *   Experiência de usuário consistente que fortalece a marca do produto.

*   **Negativas ou Riscos a Mitigar:**
    *   **Curva de Aprendizagem:** A equipe de desenvolvimento precisará ter ou adquirir proficiência em Dart e na arquitetura do Flutter (ex: gerenciamento de estado com BLoC/Riverpod).
    *   **Tamanho do Aplicativo:** O tamanho final de um aplicativo Flutter ("Hello World") é maior do que o de um aplicativo totalmente nativo, devido à inclusão do motor de renderização. No entanto, para uma aplicação complexa como o CartaOS, essa diferença se torna proporcionalmente menos significativa.
    *   **Integrações Nativas Específicas:** Para funcionalidades que dependem de APIs de baixo nível de um sistema operacional específico, será necessário desenvolver "Platform Channels", o que adiciona uma camada de complexidade. Isso deve ser mapeado e planejado para funcionalidades como a invocação de scripts locais no modo gratuito.
