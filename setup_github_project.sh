#!/bin/bash

# Script para configurar as labels e milestones do projeto CartaOS no GitHub
#
# Instruções:
# 1. Certifique-se de que você tem o GitHub CLI (`gh`) instalado e autenticado.
#    - Instalação: https://github.com/cli/cli#installation
#    - Autenticação: `gh auth login`
# 2. Navegue até o diretório raiz do seu repositório local.
# 3. Execute este script: `./setup_github_project.sh`

# Navegar para o diretório do projeto
cd /home/luis/CartaOS

# Deletar labels padrão
gh label delete "bug" --yes
gh label delete "documentation" --yes
gh label delete "duplicate" --yes
gh label delete "enhancement" --yes
gh label delete "good first issue" --yes
gh label delete "help wanted" --yes
gh label delete "invalid" --yes
gh label delete "question" --yes
gh label delete "wontfix" --yes

# Criar novas labels

# Labels de Tipo de Issue
gh label create "epic" --color "#3A0CA3" --description "Para issues que representam um épico de alto nível." --force
gh label create "user-story" --color "#4361EE" --description "Para issues que representam uma história de usuário." --force
gh label create "bug" --color "#D0021B" --description "Para issues que relatam um bug no software." --force
gh label create "feature" --color "#4CC9F0" --description "Para issues que solicitam uma nova funcionalidade." --force
gh label create "task" --color "#F72585" --description "Para tarefas técnicas que não são diretamente visíveis para o usuário." --force
gh label create "chore" --color "#7209B7" --description "Para tarefas de manutenção e outras tarefas que não se encaixam em outras categorias." --force
gh label create "documentation" --color "#B5179E" --description "Para issues relacionadas à escrita ou atualização da documentação." --force

# Labels de Prioridade
gh label create "priority:high" --color "#FF0000" --description "Para issues que devem ser resolvidas com urgência." --force
gh label create "priority:medium" --color "#FF8C00" --description "Para issues que são importantes, mas não urgentes." --force
gh label create "priority:low" --color "#FFD700" --description "Para issues que podem ser resolvidas quando houver tempo." --force

# Labels de Status
gh label create "status:open" --color "#F8F9FA" --description "Para issues que estão abertas e prontas para serem trabalhadas." --force
gh label create "status:in-progress" --color "#2196F3" --description "Para issues que estão sendo trabalhadas ativamente." --force
gh label create "status:in-review" --color "#9C27B0" --description "Para issues que foram concluídas e estão aguardando revisão." --force
gh label create "status:closed" --color "#4CAF50" --description "Para issues que foram resolvidas e fechadas." --force
gh label create "status:blocked" --color "#E91E63" --description "Para issues que estão bloqueadas por outras issues ou dependências externas." --force

# Labels de Componente/Área
gh label create "component:frontend" --color "#00BCD4" --description "Para issues relacionadas à aplicação cliente Flutter." --force
gh label create "component:backend" --color "#FFC107" --description "Para issues relacionadas à API do backend e serviços." --force
gh label create "component:database" --color "#FF9800" --description "Para issues relacionadas ao banco de dados." --force
gh label create "component:auth" --color "#673AB7" --description "Para issues relacionadas à autenticação de usuário." --force
gh label create "component:pipeline" --color "#3F51B5" --description "Para issues relacionadas ao pipeline de processamento de documentos." --force
gh label create "component:ui/ux" --color "#03A9F4" --description "Para issues relacionadas ao design da interface do usuário e experiência do usuário." --force

# Tags Adicionais
gh label create "good first issue" --color "#7057ff" --description "Para issues que são adequadas para novos contribuidores." --force
gh label create "help wanted" --color "#008672" --description "Para issues em que a equipe do projeto gostaria de ajuda da comunidade." --force
gh label create "question" --color "#d876e3" --description "Para issues que fazem uma pergunta ou buscam esclarecimentos." --force
gh label create "wontfix" --color "#ffffff" --description "Para issues que não serão corrigidas ou implementadas." --force

# Criar novos milestones
gh milestone create "Minimum Viable Product (MVP)" --description "Validar a hipótese central do CartaOS, que é agregar valor ao fluxo de trabalho de um pesquisador, automatizando o processamento e o enriquecimento semântico de documentos em uma única aplicação desktop."
gh milestone create "Sincronização na Nuvem e Melhorias na IA" --description "Introduzir a sincronização de dados na nuvem e aprimorar as capacidades de IA do CartaOS."
gh milestone create "Colaboração e Ecossistema" --description "Lançar funcionalidades colaborativas e o marketplace de plugins."