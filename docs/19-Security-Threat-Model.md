# Modelo de Ameaças de Segurança (Security Threat Model) - CartaOS v2

## 1. Introdução

Este documento descreve as potenciais ameaças de segurança ao ecossistema CartaOS e as estratégias de mitigação planejadas. O objetivo é identificar e abordar proativamente os riscos de segurança em todo o design da aplicação, em vez de reagir a eles após o fato. Usaremos o modelo **STRIDE** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) como framework para a análise.

## 2. Ativos e Pontos de Confiança

*   **Ativos Críticos:**
    *   Dados do usuário (e-mail, senha hash).
    *   Conteúdo dos documentos dos usuários (pesquisa confidencial).
    *   Chaves de API (Gemini, Stripe, etc.) tanto do sistema quanto dos usuários.
    *   Dados de pagamento (gerenciados pelo Stripe, mas o fluxo é um ponto de confiança).
    *   Código-fonte e integridade da aplicação.
*   **Superfícies de Ataque:**
    *   Aplicação cliente (Flutter).
    *   API do Backend.
    *   Banco de Dados.
    *   Infraestrutura de nuvem (Storage, etc.).
    *   Processo de autenticação.

## 3. Análise de Ameaças e Mitigações (STRIDE)

### S - Spoofing (Falsificação de Identidade)
*   **Ameaça:** Um ator malicioso se passa por um usuário legítimo para ganhar acesso à sua conta.
*   **Cenário de Ataque:** Phishing para roubar credenciais; ataque de força bruta no login.
*   **Mitigações:**
    1.  **Armazenamento Seguro de Senhas:** Usar `bcrypt` para hashear senhas no banco de dados.
    2.  **Autenticação Multifator (MFA):** Implementar MFA (via app autenticador ou e-mail) como uma opção de segurança crucial para os usuários (Pós-MVP, mas planejado).
    3.  **Rate Limiting:** Limitar o número de tentativas de login falhas por endereço IP.
    4.  **E-mails de Segurança:** Enviar e-mails de notificação para o usuário em caso de logins de novos dispositivos.

### T - Tampering (Adulteração de Dados)
*   **Ameaça:** Um invasor modifica dados em trânsito ou em repouso.
*   **Cenário de Ataque:** Ataque Man-in-the-Middle (MitM) para alterar a comunicação API; alteração direta de um documento no Cloud Storage.
*   **Mitigações:**
    1.  **Comunicação Criptografada:** Forçar o uso de HTTPS (TLS 1.2+) para toda a comunicação entre o cliente e o backend.
    2.  **Validação de Dados no Backend:** O backend deve re-validar todos os dados recebidos do cliente, nunca confiando neles implicitamente.
    3.  **URLs Assinadas e Controle de Acesso:** O acesso ao Cloud Storage deve ser feito exclusivamente através de URLs assinadas de curta duração geradas pelo backend. As políticas de IAM devem ser restritivas.
    4.  **Checksums de Arquivos:** Calcular e verificar o hash (ex: SHA-256) de um arquivo no momento do upload e antes do processamento para garantir sua integridade.

### R - Repudiation (Negação de Autoria)
*   **Ameaça:** Um usuário (legítimo ou malicioso) realiza uma ação e depois nega tê-la feito.
*   **Cenário de Ataque:** Um usuário deleta um documento importante e alega que foi uma falha do sistema.
*   **Mitigações:**
    1.  **Logs de Auditoria (Audit Trails):** Manter logs detalhados e imutáveis para ações críticas (login, upload, deleção, alteração de assinatura). Cada log deve conter o `user_id`, o endereço IP e o timestamp.
    2.  **Confirmação de Ações Destrutivas:** Exigir que o usuário confirme ações críticas e irreversíveis (ex: "Você tem certeza que quer deletar este documento? Esta ação não pode ser desfeita.").

### I - Information Disclosure (Divulgação de Informação)
*   **Ameaça:** Exposição de informações sensíveis a partes não autorizadas.
*   **Cenário de Ataque:** Vazamento de dados do banco de dados; um usuário acessando documentos de outro; exposição de chaves de API no código do cliente.
*   **Mitigações:**
    1.  **Controle de Acesso Rigoroso:** Cada requisição à API deve verificar se o usuário autenticado tem permissão para acessar o recurso solicitado (ex: `SELECT * FROM documents WHERE id = ? AND user_id = ?`).
    2.  **Criptografia em Repouso:** Garantir que o provedor de nuvem criptografe os dados no banco de dados e no storage.
    3.  **Gerenciamento de Segredos:** NUNCA armazenar chaves de API, senhas de banco de dados ou outros segredos no código-fonte. Usar um serviço de gerenciamento de segredos (como Google Secret Manager ou HashiCorp Vault).
    4.  **Segurança no Cliente:** Usar `flutter_secure_storage` para armazenar tokens no dispositivo. O código do cliente não deve conter segredos do sistema.

### D - Denial of Service (Negação de Serviço - DoS)
*   **Ameaça:** Sobrecarregar o sistema para torná-lo indisponível para usuários legítimos.
*   **Cenário de Ataque:** Um script malicioso faz milhares de uploads de arquivos ou chamadas de API de processamento; um arquivo "bomba de descompressão" é enviado para o pipeline de OCR.
*   **Mitigações:**
    1.  **Rate Limiting e Throttling:** Aplicar limites estritos na API para o número de requisições por usuário em um determinado período de tempo.
    2.  **Validação de Uploads:** Limitar o tamanho máximo dos arquivos de upload. Analisar os arquivos em um ambiente de sandbox para detectar características maliciosas antes do processamento completo.
    3.  **Escalabilidade Automática:** Usar uma arquitetura (como GKE ou Cloud Run) que possa escalar horizontalmente para absorver picos de tráfego, isolando o impacto.
    4.  **Filas Assíncronas:** O processamento pesado é feito por workers assíncronos, protegendo a API principal de sobrecarga.

### E - Elevation of Privilege (Elevação de Privilégio)
*   **Ameaça:** Um usuário com permissões limitadas consegue obter acesso a funcionalidades de um nível superior.
*   **Cenário de Ataque:** Um usuário do plano gratuito consegue acessar uma funcionalidade do plano "Lab" explorando uma falha na lógica da API; um usuário comum consegue acesso a um painel de administração.
*   **Mitigações:**
    1.  **Autorização Baseada em Claims (Claims-Based Authorization):** O JWT do usuário deve conter "claims" (alegações) sobre seu nível de assinatura e permissões. O backend deve validar esses claims em cada endpoint relevante, não confiando em parâmetros enviados pelo cliente.
    2.  **Princípio do Menor Privilégio:** Cada componente do sistema deve ter apenas as permissões estritamente necessárias para realizar sua função.
    3.  **Separação de Interfaces:** Interfaces administrativas (se existirem) devem ser completamente separadas da API pública e protegidas por múltiplos fatores de autenticação.
