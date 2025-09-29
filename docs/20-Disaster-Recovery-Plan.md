# Plano de Recuperação de Desastres (Disaster Recovery Plan) - CartaOS v2

## 1. Objetivo e Escopo

Este documento descreve as políticas e procedimentos para garantir a continuidade dos negócios e a recuperação de dados do CartaOS em caso de um desastre. Um "desastre" pode incluir falhas de hardware, corrupção de dados, falha catastrófica do provedor de nuvem em uma região, ou um ataque de segurança bem-sucedido.

O escopo deste plano cobre os dados críticos dos usuários armazenados na nossa infraestrutura de nuvem (planos "Researcher" e "Lab"), incluindo o banco de dados e o armazenamento de arquivos.

## 2. Objetivos de Recuperação (RTO e RPO)

Nossos objetivos definem a rapidez com que precisamos recuperar o serviço e a quantidade máxima de perda de dados que consideramos aceitável.

*   **RTO (Recovery Time Objective - Objetivo de Tempo de Recuperação):**
    *   **Definição:** O tempo máximo que o serviço pode ficar indisponível após um desastre.
    *   **Meta:** **4 horas.** Isso significa que, em caso de uma falha total, nos comprometemos a ter o serviço restaurado e operacional em até 4 horas.

*   **RPO (Recovery Point Objective - Objetivo de Ponto de Recuperação):**
    *   **Definição:** A quantidade máxima de dados que pode ser perdida, medida em tempo.
    *   **Meta:** **15 minutos.** Isso significa que, no pior cenário, perderíamos no máximo os últimos 15 minutos de dados gerados ou modificados antes do desastre.

## 3. Estratégia de Backup e Redundância

Para atingir nossos objetivos de RTO e RPO, implementaremos uma estratégia de backup e redundância em múltiplas camadas.

### 3.1. Banco de Dados (PostgreSQL)

*   **PITR (Point-in-Time Recovery):**
    *   **Estratégia:** Utilizaremos a funcionalidade de backup contínuo e arquivamento de WAL (Write-Ahead Logging) do PostgreSQL, gerenciada pelo nosso provedor de nuvem (ex: Google Cloud SQL ou AWS RDS).
    *   **Frequência:** Contínua. Cada transação é registrada.
    *   **Como atinge o RPO:** Permite-nos restaurar o banco de dados para qualquer ponto no tempo nos últimos (pelo menos) 7 dias, com uma granularidade de segundos. Isso facilmente atende ao nosso RPO de 15 minutos.

*   **Snapshots Diários:**
    *   **Estratégia:** Além do PITR, snapshots completos do banco de dados serão tirados automaticamente a cada 24 horas.
    *   **Retenção:** Os snapshots serão retidos por pelo menos 30 dias.
    *   **Propósito:** Fornecem uma camada adicional de segurança e são úteis para criar ambientes de teste ou para recuperações de desastres mais antigos.

### 3.2. Armazenamento de Arquivos (Cloud Storage - GCS/S3)

*   **Versionamento de Objetos:**
    *   **Estratégia:** A funcionalidade de versionamento será ativada em todos os buckets de armazenamento. Isso significa que, quando um arquivo é sobrescrito ou deletado, a versão antiga não é removida imediatamente, mas se torna uma versão não-corrente.
    *   **Propósito:** Protege contra deleções acidentais ou modificações maliciosas. Podemos restaurar uma versão anterior de qualquer arquivo.

*   **Replicação Multi-Regional:**
    *   **Estratégia:** Os buckets de armazenamento serão configurados para serem multi-regionais. O provedor de nuvem replicará automaticamente os dados em data centers geograficamente distintos.
    *   **Como atinge o RTO:** Se um data center ou uma região inteira ficar indisponível, o tráfego pode ser redirecionado para outra região onde os dados já estão replicados, minimizando o tempo de inatividade.

## 4. Procedimento de Recuperação de Desastres

Em caso de um desastre declarado, a seguinte sequência de ações será iniciada pela equipe de engenharia:

1.  **Declaração do Incidente (T+0m):** O engenheiro de plantão declara um incidente de Nível 1, notificando toda a equipe de liderança e engenharia.

2.  **Avaliação (T+0 a T+30m):** A equipe avalia a extensão do dano. O desastre é total (ex: perda de uma região inteira) ou parcial (ex: corrupção de uma tabela no DB)?

3.  **Decisão de Failover (T+30m):** Com base na avaliação, a decisão de iniciar o processo de failover para uma região secundária é tomada.

4.  **Restauração do Banco de Dados (T+30m a T+2h):**
    *   Um novo cluster de banco de dados é provisionado na região secundária.
    *   O banco de dados é restaurado a partir do backup PITR para o ponto mais recente possível antes do desastre (atendendo ao RPO de 15 minutos).

5.  **Redirecionamento de Tráfego (T+2h a T+3h):**
    *   As configurações de DNS são atualizadas para apontar a API do CartaOS para os novos servidores na região secundária.
    *   Como o armazenamento de arquivos já é multi-regional, os dados dos usuários estarão disponíveis assim que a API e o banco de dados estiverem online.

6.  **Validação e Verificação (T+3h a T+4h):**
    *   A equipe realiza uma série de testes automatizados e manuais para garantir que o sistema está totalmente funcional no novo ambiente.
    *   O serviço é declarado operacional e a comunicação é enviada aos usuários.

## 5. Testes do Plano de Recuperação

Um plano de recuperação de desastres só é útil se for testado.

*   **Frequência:** A equipe de engenharia realizará um exercício completo de recuperação de desastres **a cada 6 meses**.
*   **Procedimento do Teste:** Um ambiente de teste, que é uma réplica da produção, será usado. A equipe simulará uma falha e seguirá o procedimento de recuperação passo a passo, medindo o tempo real para restaurar o serviço.
*   **Pós-Teste:** Após cada teste, um relatório de "post-mortem" será escrito para identificar quaisquer lacunas no plano e implementar melhorias.
