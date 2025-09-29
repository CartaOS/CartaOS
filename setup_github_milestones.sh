#!/bin/bash

# Script para configurar os milestones do projeto CartaOS no GitHub

# Navegar para o diretório do projeto
cd /home/luis/CartaOS

# Criar novos milestones
gh api -X POST /repos/CartaOS/CartaOS/milestones -f title='Minimum Viable Product (MVP)' -f description='Validar a hipótese central do CartaOS, que é agregar valor ao fluxo de trabalho de um pesquisador, automatizando o processamento e o enriquecimento semântico de documentos em uma única aplicação desktop.'
gh api -X POST /repos/CartaOS/CartaOS/milestones -f title='Sincronização na Nuvem e Melhorias na IA' -f description='Introduzir a sincronização de dados na nuvem e aprimorar as capacidades de IA do CartaOS.'
gh api -X POST /repos/CartaOS/CartaOS/milestones -f title='Colaboração e Ecossistema' -f description='Lançar funcionalidades colaborativas e o marketplace de plugins.'
