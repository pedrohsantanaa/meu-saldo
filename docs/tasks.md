# tasks.md --- meuSaldo

**Projeto:** meuSaldo --- Controle Financeiro Pessoal\
**Versão:** 0.1 --- Plano inicial de implementação do MVP\
**Documentos de referência:** `requirements.md`, `spec.md` e `design.md`

------------------------------------------------------------------------

## 1. Objetivo

Este documento divide o desenvolvimento do meuSaldo em tarefas pequenas,
ordenadas por dependência e prioridade. Cada tarefa deverá produzir uma
entrega verificável.

A implementação deverá seguir os requisitos, as regras de negócio e a
arquitetura descritos nos documentos de referência. Não implementar
regras financeiras que ainda estejam marcadas como pendentes sem antes
obter uma decisão do responsável pelo produto.

## 2. Decisões de produto consideradas

As tarefas consideram as seguintes decisões confirmadas:

-   O usuário poderá cadastrar e gerenciar vários cartões de crédito.
-   Os orçamentos serão definidos por cartão, categoria e mês.
-   A visão geral terá **duas visualizações**: mensal e anual.
-   A visão mensal apresentará os detalhes de um mês, com navegação
    entre meses.
-   A visão anual apresentará os 12 meses em colunas, permitindo
    comparação ao longo do ano.
-   A interface deverá seguir a referência visual do protótipo e a
    lógica da planilha enviada.
-   A aplicação será web, responsiva e acessível por navegador.

## 3. Convenções

-   `[ ]` Pendente.
-   `[x]` Concluída.
-   `[!]` Bloqueada por decisão ou dependência.
-   **P0:** essencial para disponibilizar o MVP.
-   **P1:** importante para completar a experiência principal.
-   **P2:** melhoria que pode ser realizada após a primeira validação.

Uma tarefa somente deverá ser marcada como concluída quando o código
estiver implementado, revisado e testado, e os critérios de conclusão
forem atendidos.

## 4. Organização sugerida do projeto

A estrutura abaixo é uma referência inicial. Ajustá-la se o `design.md`
ou a implementação justificar outra organização.

``` text
meuSaldo/
├── docs/
│   ├── requirements.md
│   ├── spec.md
│   ├── design.md
│   ├── tasks.md
│   └── acceptance.md
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── repositories/
│   ├── tests/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── router/
│   │   ├── services/
│   │   ├── stores/
│   │   └── utils/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 5. Fase 0 --- Validação das regras pendentes

**Objetivo:** resolver decisões que afetam cálculos, persistência e
comportamento antes de implementar as partes dependentes.

-   [x] **T-001 \[P0\]** Revisar os documentos e alinhar nomes e
    decisões do produto.
    -   Confirmar o nome `meuSaldo` em todos os documentos.
    -   Confirmar que a visão geral mensal e anual fazem parte do
        escopo.
    -   Confirmar múltiplos cartões e orçamento por cartão, categoria e
        mês.
    -   Registrar divergências encontradas entre `requirements.md`,
        `spec.md` e `design.md`.
    -   **Resultado:** documentos alinhados nas decisões confirmadas;
        divergências registradas na seção 15 do `spec.md`.
-   [x] **T-002 \[P0\]** Definir a política de contabilização de
    despesas e compras no cartão.
    -   Determinar qual data define o mês da despesa.
    -   Definir como compras e faturas aparecem na visão mensal e anual.
    -   Garantir que compra e pagamento da fatura não sejam
        contabilizados duas vezes.
    -   Documentar exemplos de cálculo.
    -   **Resultado:** política definida em `spec.md` §7.2, com
        exemplos na seção 7.4: movimentações comuns contam na data do
        lançamento; compras no cartão contam no ciclo da fatura,
        identificada pelo mês do vencimento (compras após o fechamento
        vão ao ciclo seguinte); a fatura é contada uma única vez e o
        pagamento é liquidação.
-   [x] **T-003 \[P0\]** Definir a relação entre mês da compra, mês da
    fatura e mês do orçamento.
    -   Decidir se o orçamento considera a data da compra ou o ciclo da
        fatura.
    -   Aplicar a mesma regra na tela de cartões e na tela de
        orçamentos.
    -   **Resultado:** decidido junto com T-002, conforme o uso do
        responsável pelo produto: o orçamento segue o ciclo da fatura
        (mês do vencimento da fatura), com regra única para cartões,
        faturas, orçamentos e relatórios (`spec.md` §7.2).
-   [x] **T-004 \[P1\]** Definir regras de fechamento e vencimento das
    faturas.
    -   Definir o tratamento de compras feitas no dia do fechamento.
    -   Definir o cálculo para meses com menos dias que o dia
        configurado.
    -   Definir como será criada a primeira fatura de um cartão.
    -   **Resultado:** definido em `spec.md` §6.10: compras no dia do
        fechamento entram no ciclo seguinte; dias inexistentes no mês
        usam o último dia do mês; a primeira fatura vai do cadastro até
        a véspera do primeiro fechamento posterior. Ver AC-103 a
        AC-105.
-   [x] **T-005 \[P1\]** Decidir se compras parceladas farão parte do
    MVP.
    -   Se aprovadas, definir distribuição de centavos e atribuição das
        parcelas às faturas.
    -   Se não aprovadas, limitar a primeira versão a compras não
        parceladas e registrar parcelamento como evolução.
    -   **Resultado:** decidido com o responsável pelo produto: sem
        parcelamento no MVP, somente compras à vista; parcelamento
        registrado como evolução futura (`spec.md` §6.9).
-   [x] **T-006 \[P1\]** Definir o cálculo do limite comprometido e
    disponível.
    -   Decidir se parcelas futuras comprometem o limite.
    -   Definir como pagamentos de fatura liberam limite.
    -   **Resultado:** definido em `spec.md` §6.11: comprometido = soma
        das compras de faturas não pagas, deduzidos os pagamentos
        registrados; pagamento total ou parcial da fatura libera o
        limite (DP-05/DD-05 resolvidas). Ver AC-106.
-   [x] **T-007 \[P1\]** Definir o escopo de recorrência de despesas
    fixas.
    -   Decidir se cada mês terá lançamentos manuais ou se haverá
        geração de despesas recorrentes.
    -   Não implementar recorrência automática sem essa decisão.
    -   **Resultado:** decidido com o responsável pelo produto: despesas
        fixas são lançadas manualmente, mês a mês; sem recorrência
        automática no MVP (`spec.md` §6.5).
-   [x] **T-008 \[P1\]** Definir categorias iniciais e tipos de
    movimentação.
    -   Separar receitas, despesas fixas, despesas variáveis e
        investimentos.
    -   Definir quais categorias padrão serão disponibilizadas.
    -   Definir se o usuário poderá criar, editar, desativar e reativar
        categorias.
    -   **Resultado:** categorias totalmente editáveis (padrão e
        próprias: criar, editar, desativar e reativar); lista de
        categorias padrão iniciais em `spec.md` §6.3. Ver AC-107.

**Critério de conclusão da fase:** decisões registradas nos documentos
de especificação e regras necessárias aos cálculos aprovadas.

**Fase 0 concluída:** todas as tarefas T-001 a T-008 foram definidas e
registradas nos documentos de especificação (`spec.md`, `design.md` e
`acceptance.md`).

## 6. Fase 1 --- Fundação do projeto e ambiente

**Objetivo:** preparar a estrutura técnica para o desenvolvimento.

-   [x] **T-009 \[P0\]** Criar o repositório Git do meuSaldo.
    -   Criar estrutura inicial de pastas.
    -   Adicionar `.gitignore`.
    -   Criar `README.md` com visão geral e instruções iniciais.
    -   **Resultado:** estrutura `backend/` + `frontend/` + `docs/`
        criada; `.gitignore` e `README.md` adicionados (o repositório
        Git já existia).
-   [x] **T-010 \[P0\]** Inicializar o back-end com Python e FastAPI.
    -   Criar aplicação principal.
    -   Configurar variáveis de ambiente.
    -   Criar endpoint de verificação de saúde, por exemplo `/health`.
    -   Configurar documentação OpenAPI.
    -   **Resultado:** API em `backend/app/main.py` com `/health`
        validado, OpenAPI em `/docs` e configuração por variáveis de
        ambiente (`app/core/config.py`, `.env.example`).
-   [x] **T-011 \[P0\]** Inicializar o front-end com Vue.js 3.
    -   Configurar Vite.
    -   Configurar Tailwind CSS.
    -   Configurar roteamento.
    -   Criar tela inicial e estrutura de layout.
    -   **Resultado:** Vue 3 + Vite + Tailwind em `frontend/`; rotas
        para as 6 seções do menu (AC-077); layout com navegação lateral
        e adaptada para móvel; build de produção validado.
-   [x] **T-012 \[P0\]** Configurar PostgreSQL.
    -   Criar banco e usuário de aplicação.
    -   Configurar conexão pelo back-end.
    -   Utilizar variáveis de ambiente para credenciais.
    -   **Resultado:** PostgreSQL 16 via Docker Compose (banco/usuário
        por variáveis) e conexão por `DATABASE_URL`; migracoes aplicadas
        com sucesso no banco real.
-   [x] **T-013 \[P0\]** Configurar migrações do banco.
    -   Integrar ferramenta de migração, como Alembic.
    -   Criar primeira migração.
    -   Documentar como aplicar e reverter migrações.
    -   **Resultado:** Alembic integrado em `backend/alembic`; revisão
        `0001_baseline` aplicada e verificada (`alembic current`);
        comandos no `README.md`.
-   [x] **T-014 \[P1\]** Preparar ambiente local com Docker Compose.
    -   Configurar serviços de front-end, back-end e banco de dados,
        conforme necessário.
    -   Configurar volumes e rede interna.
    -   Documentar comandos para subir e encerrar o ambiente.
    -   **Resultado:** `docker-compose.yml` com `db` (healthcheck e
        volume `pgdata`), `backend` e `frontend`; porta do banco
        parametrizável via `POSTGRES_PORT`; comandos no `README.md`.
-   [x] **T-015 \[P0\]** Configurar padrões de qualidade.
    -   Definir formatação e lint para Python e JavaScript.
    -   Configurar tratamento padronizado de erros.
    -   Criar configuração inicial de testes automatizados.
    -   **Resultado:** Ruff (lint/format) e pytest no back-end (2
        testes); ESLint + Prettier e Vitest no front-end (2 testes);
        erros da API com envelope padronizado `{"error": {code, message,
        details}}` (`backend/app/core/errors.py`).

**Critério de conclusão da fase:** front-end e back-end iniciam
localmente, conectam ao banco e possuem instruções reproduzíveis.

## 7. Fase 2 --- Identidade visual e estrutura de navegação

**Objetivo:** construir a base visual conforme o protótipo de
referência.

-   [x] **T-016 \[P0\]** Definir tokens visuais.
    -   Cores principais, neutras, positivas, negativas e de atenção.
    -   Tipografia, espaçamentos, bordas, sombras e raios.
    -   Estados de foco, hover, desabilitado e erro.
    -   **Resultado:** tokens em `frontend/tailwind.config.js` (primary,
        positive, negative e attention com tons claros; tipografia de
        sistema; sombras card/panel; raio card) e estados de foco,
        hover, desabilitado e erro em `src/assets/main.css` e nos
        componentes.
-   [x] **T-017 \[P0\]** Criar layout principal da aplicação.
    -   Implementar marca e nome `meuSaldo`.
    -   Criar navegação lateral para telas grandes.
    -   Criar navegação compacta para dispositivos móveis.
    -   Reservar área de conteúdo principal.
    -   **Resultado:** marca `meuSaldo` (símbolo + nome) nas navegações
        `SidebarNavigation` e `MobileNavigation`; área de conteúdo
        principal em `AppLayout`.
-   [x] **T-018 \[P0\]** Criar componentes compartilhados.
    -   Botões, campos, seletores, modais e tabelas.
    -   Cartões de indicadores.
    -   Mensagens de sucesso e erro.
    -   Estados de carregamento e listas vazias.
    -   Campo monetário com formatação brasileira.
    -   **Resultado:** `BaseButton`, `BaseInput`, `BaseSelect`,
        `BaseModal`, `ConfirmDialog`, `BaseTable`, `BaseMessage`,
        `LoadingState`, `EmptyState`, `SectionHeader`, `SummaryCard` e
        `CurrencyInput` (BRL, com testes) em `frontend/src/components`.
-   [x] **T-019 \[P1\]** Criar componentes de período.
    -   Seletor de mês e ano.
    -   Navegação para mês anterior e próximo.
    -   Seletor de ano.
    -   Alternância entre visão mensal e anual.
    -   **Resultado:** `MonthSelector` com navegação mês/ano, seletor de
        ano, botão "Hoje" e alternância mensal/anual; utilitários em
        `src/utils/period.js`; testes unitários incluídos.
-   [x] **T-020 \[P1\]** Validar responsividade do layout.
    -   Testar larguras de desktop, tablet e smartphone.
    -   Garantir navegação e formulários utilizáveis em telas pequenas.
    -   **Resultado:** breakpoints sm/md/lg aplicados (grid de
        indicadores, navegação compacta, tabelas com rolagem
        horizontal, formulários em largura total); CSS de produção
        contém os três breakpoints. Recomenda-se passada manual em
        dispositivos reais antes da publicação.

**Critério de conclusão da fase:** layout consistente, navegável e
responsivo, ainda que utilizando dados de demonstração.

**Fase 2 concluída:** layout e componentes em uso com dados de
demonstração. Verificações: ESLint limpo, 16 testes Vitest passando e
build de produção OK.

**Alinhamento visual ao protótipo (`docs/interface.png`):** todas as
telas passaram a seguir o protótipo aprovado (sidebar escura, ações em
verde, indicadores com ícone, gráficos e dados de demonstração). A
navegação também segue o protótipo: Dashboard (Visão Mensal e Visão
Anual), Movimentações, Cartões, Orçamentos, Categorias, Relatórios e
Configurações.

## 8. Fase 3 --- Banco de dados, autenticação e isolamento

**Objetivo:** implementar a base de dados e o acesso seguro dos
usuários.

-   [x] **T-021 \[P0\]** Implementar entidade e migração de usuário.
    -   Nome, e-mail, hash da senha e datas de auditoria.
    -   Garantir unicidade do e-mail.
    -   **Resultado:** `User` em `backend/app/models/user.py` e
        `AuthSession` (sessão revogável) em `app/models/auth_session.py`;
        migração `0002_user_sessions` aplicada e verificada no banco
        real; e-mail com índice único.
-   [x] **T-022 \[P0\]** Implementar cadastro de usuário.
    -   Validar campos.
    -   Validar e-mail único.
    -   Armazenar senha com hash seguro.
    -   **Resultado:** `POST /api/auth/register` (`app/services/auth.py`):
        validação com Pydantic (senha com mínimo de 8 caracteres), e-mail
        único (409 com envelope padrão) e hash bcrypt. Ver testes em
        `tests/test_auth.py`.
-   [x] **T-023 \[P0\]** Implementar login e logout.
    -   Validar credenciais.
    -   Configurar mecanismo de sessão ou token.
    -   Definir armazenamento e expiração de credenciais.
    -   Implementar encerramento da sessão.
    -   **Resultado:** `POST /api/auth/login` emite JWT (expiração
        configurável, padrão 60 min) vinculado a uma sessão revogável
        (`auth_sessions`); logout revoga a sessão imediatamente (AC-008
        verificado ponta a ponta); mensagens genéricas de credenciais
        (AC-006).
-   [x] **T-024 \[P0\]** Proteger rotas do front-end e endpoints
    privados.
    -   Redirecionar usuários não autenticados.
    -   Validar autorização no back-end.
    -   **Resultado:** dependência `get_current_user`
        (`backend/app/api/deps.py`) exigida nas rotas privadas (401 com
        envelope padrão); guarda de rotas no vue-router redireciona para
        `/login` com retorno à rota original; páginas `LoginPage` e
        `RegisterPage` na identidade visual; token enviado pelo
        `services/api.js`.
-   [x] **T-025 \[P0\]** Implementar isolamento dos dados por usuário.
    -   Aplicar o usuário autenticado nas consultas.
    -   Impedir acesso a registros de outro usuário por alteração de
        IDs.
    -   Criar testes de autorização.
    -   **Resultado:** `get_current_user` é a única fonte de escopo de
        usuário para as rotas privadas (padrão para as próximas fases);
        testes de autorização em `tests/test_auth.py` (token inválido,
        sem token, logout revoga sessão, isolamento entre usuários).
        A validação de AC-009 com recursos de negócio será ampliada nas
        fases 4 a 7.
-   [x] **T-026 \[P1\]** Implementar recuperação de senha, caso aprovada
    para o MVP.
    -   Definir envio de e-mail.
    -   Criar fluxo seguro de redefinição.
    -   Não revelar se determinado e-mail está cadastrado.
    -   **Resultado:** DP-08 aprovada pelo responsável. Fluxo
        implementado: `POST /api/auth/forgot-password` (resposta
        genérica) e `POST /api/auth/reset-password` com token de uso
        único (hash SHA-256 no banco, expiração de 30 min), que encerra
        todas as sessões ao redefinir a senha. Envio de e-mail
        configurável (console em desenvolvimento, SMTP em produção) e
        telas "Esqueci minha senha" e "Redefinir senha". Ver AC-108 a
        AC-110.

**Critério de conclusão da fase:** usuário consegue criar conta e
acessar áreas privadas; testes comprovam isolamento dos dados.

## 9. Fase 4 --- Categorias e movimentações financeiras

**Objetivo:** permitir registrar e consultar as informações que
alimentam o controle financeiro.

### Categorias

-   [x] **T-027 \[P0\]** Criar modelo e migrações de categorias.
    -   Suportar categorias padrão e categorias do usuário.
    -   Suportar grupos receita, despesa e investimento.
    -   Suportar classificação fixa ou variável para despesas.
    -   Suportar ativação e desativação.
    -   **Resultado:** modelo `Category` (com `is_default`, grupos e
        classificação) e migração `0004_categories_transactions`; as
        categorias padrão do sistema (`spec.md` §6.3) são criadas como
        cópias do usuário na inscrição e são totalmente editáveis.
-   [x] **T-028 \[P0\]** Implementar API e interface de categorias.
    -   Listar, criar e editar categorias.
    -   Ativar e desativar categorias.
    -   Impedir incompatibilidade entre categoria e tipo de
        movimentação.
    -   **Resultado:** `GET/POST/PUT /api/categories` e
        `PATCH /api/categories/{id}/status`; nome único por usuário e
        grupo (409); validação de grupo/classificação; tela de
        Categorias com filtros, criação/edição em modal e desativação
        com confirmação (preserva histórico, AC-014).

### Receitas

-   [x] **T-029 \[P0\]** Criar modelo e API de receitas.
    -   Descrição, valor, data, categoria e observações.
    -   Validar valor positivo e categoria compatível.
    -   Associar ao usuário autenticado.
    -   **Resultado:** modelo `Transaction` (receita, despesa e
        investimento) e `POST /api/transactions` com valor > 0 (AC-016),
        categoria compatível (AC-012) e escopo por usuário.
-   [x] **T-030 \[P0\]** Criar formulário e listagem de receitas.
    -   Cadastrar, editar e excluir.
    -   Apresentar mensagens de validação.
    -   Atualizar informações após salvar.
    -   **Resultado:** `TransactionForm` (modal) e listagem na tela de
        Movimentações, com mensagens de erro do envelope padrão e
        recarga após salvar/excluir.

### Despesas

-   [x] **T-031 \[P0\]** Criar modelo e API de despesas.
    -   Descrição, valor, data, categoria, forma de pagamento e
        observações.
    -   Classificação fixa ou variável.
    -   Validar valor e categoria.
    -   **Resultado:** campos no modelo `Transaction`; despesas exigem
        classificação fixa/variável (AC-022) e forma de pagamento
        (dinheiro, pix, débito ou outra --- cartão de crédito entra na
        Fase 6, com o cadastro de cartões).
-   [x] **T-032 \[P0\]** Criar formulário e listagem de despesas.
    -   Cadastrar, editar e excluir.
    -   Exibir forma de pagamento e classificação.
    -   Atualizar informações após salvar.
    -   **Resultado:** mesmos fluxos de T-030, exibindo classificação e
        forma de pagamento na listagem.

### Investimentos

-   [x] **T-033 \[P1\]** Implementar registro de investimentos.
    -   Descrição, valor, data, categoria ou objetivo.
    -   Apresentar investimentos em seção própria.
    -   Considerar investimentos no cálculo do restante conforme regra
        aprovada.
    -   **Resultado:** tipo `investment` no modelo e na API, com
        categorias próprias (ex.: Poupança) e badge distinto na
        listagem; o cálculo do restante é da Fase 5 (AC-025).

### Histórico

-   [x] **T-034 \[P0\]** Criar tela de movimentações.
    -   Listar registros por data.
    -   Filtrar por período, tipo, categoria e forma de pagamento.
    -   Oferecer ações de edição e exclusão.
    -   Exibir estado vazio e filtros sem resultado.
    -   **Resultado:** tela de Movimentações com dados persistidos,
        ordenação por data (mais recentes primeiro, AC-027), filtros
        combináveis (período via MonthSelector, tipo, categoria, forma
        de pagamento e busca), edição/exclusão com confirmação (AC-081)
        e estados vazios.

**Critério de conclusão da fase:** usuário consegue registrar, editar,
excluir, filtrar e consultar seus registros financeiros com dados
persistidos.

**Fase 4 concluída:** critério atendido, verificado ponta a ponta com
Postgres real (migração `0004`, seed de 27 categorias padrão, CRUD de
movimentações e filtros). Testes: 40 no back-end (incluindo isolamento
por usuário com dados reais, AC-009) e 21 no front-end.

## 10. Fase 5 --- Visão geral mensal e anual

**Objetivo:** transformar a visão principal da planilha em duas
visualizações integradas.

### Visão mensal

-   [x] **T-035 \[P0\]** Implementar serviço de resumo mensal no
    back-end.
    -   Total de receitas.
    -   Total de despesas fixas.
    -   Total de despesas variáveis.
    -   Total de investimentos.
    -   Total de saídas.
    -   Restante do mês.
    -   Aplicar a política de contabilização aprovada.
    -   **Resultado:** `app/services/dashboard.py` com as fórmulas
        aprovadas (`saídas = fixas + variáveis + investimentos`;
        `restante = receitas − saídas`, AC-025/AC-033/AC-034), valores
        normalizados em duas casas decimais (spec §7.3) e agrupamentos
        por categoria.
-   [x] **T-036 \[P0\]** Implementar API do dashboard mensal.
    -   Receber mês e ano.
    -   Retornar indicadores e itens agrupados.
    -   Retornar últimas movimentações, se aplicável.
    -   **Resultado:** `GET /api/dashboard/monthly?month=AAAA-MM` com
        indicadores, grupos (receitas, fixas, variáveis, investimentos),
        despesas por categoria, últimas movimentações e tendência de 6
        meses para o gráfico.
-   [x] **T-037 \[P0\]** Implementar interface da visão mensal.
    -   Seletor de mês e ano.
    -   Indicadores financeiros.
    -   Seções de contas a receber, despesas fixas, despesas variáveis e
        investimentos.
    -   Resumo do mês.
    -   Acesso rápido para adicionar movimentação.
    -   **Resultado:** `VisaoMensalPage` com dados reais: indicadores,
        gráficos (composição e tendência), as quatro seções de grupos,
        últimas movimentações e botão que abre o formulário em
        `/movimentacoes?novo=1`.
-   [x] **T-038 \[P0\]** Implementar navegação entre meses.
    -   Mês anterior.
    -   Próximo mês.
    -   Retorno ao mês atual.
    -   Preservar o contexto ao alternar de visualização.
    -   **Resultado:** `MonthSelector` com anterior/próximo/"Hoje" e
        parâmetro `?month=AAAA-MM` preservando o contexto vindo da visão
        anual.

### Visão anual

-   [x] **T-039 \[P1\]** Implementar serviço de resumo anual no
    back-end.
    -   Receber ano selecionado.
    -   Calcular os totais de cada mês.
    -   Agrupar receitas, despesas fixas, despesas variáveis e
        investimentos.
    -   Calcular restante de cada mês.
    -   Evitar duplicidade de compras e faturas.
    -   **Resultado:** `annual_summary` em `app/services/dashboard.py`;
        sem compras de cartão até a Fase 6, não há risco de duplicidade
        com faturas (política registrada em `spec.md` §7.2).
-   [x] **T-040 \[P1\]** Implementar API do dashboard anual.
    -   Retornar os 12 meses, inclusive meses sem movimentação.
    -   Retornar totais anuais e valores por grupo.
    -   Garantir ordenação cronológica.
    -   **Resultado:** `GET /api/dashboard/annual?year=AAAA` com os 12
        meses (zeros nos meses vazios, AC-041) em ordem cronológica e
        totais anuais.
-   [x] **T-041 \[P1\]** Implementar interface da visão anual.
    -   Apresentar meses em colunas.
    -   Apresentar grupos financeiros em linhas.
    -   Exibir totais mensais e anuais.
    -   Permitir selecionar um mês para abrir sua visão mensal.
    -   Permitir navegar entre anos.
    -   **Resultado:** `VisaoAnualPage` com tabela de 12 meses, gráfico
        de evolução, "Totais do Ano", seletor de ano e clique em qualquer
        mês abrindo a visão mensal correspondente.
-   [x] **T-042 \[P1\]** Implementar alternância mensal/anual.
    -   Manter o ano selecionado.
    -   Preservar o mês de referência quando fizer sentido.
    -   Exibir claramente qual visualização está ativa.
    -   **Resultado:** alternância pelo menu (item ativo destacado na
        navegação); o mês de referência viaja pelo parâmetro `?month`.
-   [x] **T-043 \[P1\]** Validar visão anual em telas menores.
    -   Implementar rolagem horizontal controlada ou apresentação
        compacta.
    -   Evitar truncamento de valores.
    -   Manter os meses identificáveis.
    -   **Resultado:** tabela com rolagem horizontal e largura mínima
        preservando os 12 meses identificáveis; valores sem truncamento
        (algarismos tabulares). Recomenda-se passada manual em telas
        pequenas junto com a revisão de usabilidade (T-066).

**Critério de conclusão da fase:** os dados da visão mensal e anual são
consistentes entre si; selecionar um mês na visão anual abre o resumo
mensal correspondente.

**Fase 5 concluída:** consistência mensal × anual verificada em teste
automatizado e ponta a ponta com Postgres real; clique no mês da visão
anual abre a visão mensal. Testes: 47 no back-end e 21 no front-end.

## 11. Fase 6 --- Múltiplos cartões, compras e faturas

**Objetivo:** implementar o controle de vários cartões de crédito por
usuário.

-   [x] **T-044 \[P0\]** Criar modelo e migrações de cartões.
    -   Nome, emissor opcional, limite, fechamento, vencimento e
        situação.
    -   Associar cada cartão ao usuário.
    -   Não armazenar número completo, CVV ou senha.
-   [x] **T-045 \[P0\]** Implementar API e interface de cartões.
    -   Listar, cadastrar, editar e inativar.
    -   Exibir limite e dados básicos.
    -   Impedir compras em cartões inativos.
-   [x] **T-046 \[P0\]** Criar modelo de compras no cartão.
    -   Cartão, categoria, descrição, data e valor.
    -   Associar compra ao usuário e cartão.
    -   Validar compatibilidade de propriedade dos registros.
-   [x] **T-047 \[P0\]** Implementar cadastro e histórico de compras.
    -   Registrar compra em cartão selecionado.
    -   Listar compras por cartão e período.
    -   Editar e excluir compras.
    -   Atualizar valores de orçamento relacionados.
-   [x] **T-048 \[P0\]** Implementar cálculo do ciclo de fatura.
    -   Considerar fechamento e vencimento.
    -   Tratar virada de mês e meses com duração diferente.
    -   Aplicar a regra aprovada para compras no dia do fechamento.
-   [x] **T-049 \[P0\]** Implementar entidades e API de faturas.
    -   Agrupar compras no ciclo correto.
    -   Calcular total da fatura.
    -   Consultar fatura atual, próxima e histórico.
    -   Evitar duplicidade no resumo financeiro.
-   [x] **T-050 \[P1\]** Implementar acompanhamento de limite.
    -   Calcular valor comprometido.
    -   Calcular limite disponível.
    -   Aplicar a política aprovada para parcelas e pagamentos.
-   [x] **T-051 \[P1\]** Implementar pagamento de fatura, se aprovado.
    -   Registrar pagamento total ou parcial.
    -   Tratar pagamento como liquidação da obrigação.
    -   Não criar uma segunda despesa de consumo.
-   [!] **T-052 \[P1\]** Implementar parcelamento, se aprovado para o
    MVP.
    -   Distribuir parcelas entre faturas.
    -   Garantir soma exata do valor original.
    -   Tratar diferenças de centavos.
    -   Atualizar limite e orçamento conforme regras aprovadas.
    -   **Adiada:** o parcelamento não foi aprovado para o MVP (decisão
        T-005); fica como evolução futura.

**Critério de conclusão da fase:** o usuário consegue gerenciar vários
cartões, registrar compras e consultar faturas; os cálculos não duplicam
despesas.

**Fase 6 concluída:** cartões, compras, faturas e pagamentos
implementados com a política de contabilização aprovada (T-002/T-004):
a compra conta no mês do vencimento da fatura e entra uma única vez nas
despesas variáveis do resumo; o pagamento é liquidação (não gera nova
despesa) e libera o limite (T-050/T-051). A atribuição da compra à
fatura é fixada no registro (snapshot): alterar os dias de
fechamento/vencimento não move compras já registradas. O item de
orçamento de T-047 será composto a partir das compras na Fase 7.
Parcelamento fora do MVP (T-052). Testes: 94 no back-end e 24 no
front-end.

**Melhoria (pós-Fase 8):** a cor do cartão é escolhida pelo usuário no
cadastro/edição — seletor grande com paleta de 19 tons (`ColorPicker`),
em vez de gradiente gerado por id; cartões anteriores mantêm o
gradiente por id até serem editados.

## 12. Fase 7 --- Orçamentos por cartão e categoria

**Objetivo:** implementar a funcionalidade baseada na segunda planilha
enviada.

-   [x] **T-053 \[P0\]** Criar modelo e migração de orçamento por
    cartão.
    -   Usuário.
    -   Cartão.
    -   Categoria.
    -   Mês de referência.
    -   Valor planejado.
    -   Restrição de unicidade para usuário + cartão + categoria + mês.
-   [x] **T-054 \[P0\]** Implementar API de consulta de orçamentos.
    -   Receber mês e cartão.
    -   Listar categorias orçadas.
    -   Retornar valor planejado, gastos e restante.
    -   Retornar categorias sem orçamento como "Não definido", sem
        assumir zero.
-   [x] **T-055 \[P0\]** Implementar criação, edição e exclusão de
    orçamentos.
    -   Validar cartão e categoria pertencentes ao usuário.
    -   Impedir orçamento duplicado para a mesma combinação.
    -   Validar valores não negativos.
-   [x] **T-056 \[P0\]** Implementar tela de orçamentos.
    -   Seleção de mês.
    -   Seleção de cartão.
    -   Tabela com categoria, orçamento, gastos e restante.
    -   Totalizador.
    -   Ação para novo orçamento.
-   [x] **T-057 \[P0\]** Implementar cálculo de gastos por categoria.
    -   Considerar somente compras do cartão e mês conforme política
        aprovada.
    -   Atualizar totais após inclusão, edição ou exclusão de compra.
    -   Evitar somar pagamento de fatura como nova compra.
-   [x] **T-058 \[P1\]** Implementar indicadores de utilização.
    -   Dentro do orçamento.
    -   Próximo do limite.
    -   Orçamento ultrapassado.
    -   Calcular percentual somente quando houver orçamento maior que
        zero.
    -   Utilizar o percentual de alerta aprovado.
-   [x] **T-059 \[P1\]** Permitir iniciar compra a partir de uma
    categoria orçada.
    -   Abrir formulário com cartão e categoria preenchidos.
    -   Após salvar, atualizar gastos e restante.

**Critério de conclusão da fase:** para cada cartão e mês, o usuário
consegue definir orçamento por categoria e acompanhar planejado, gasto e
restante corretamente.

**Fase 7 concluída:** orçamento por usuário + cartão + mês + categoria
(unicidade garantida); gastos calculados pelo ciclo da fatura (mês do
vencimento), sempre derivados das compras — inclusão, edição e exclusão
de compra atualizam o orçamento automaticamente e o pagamento de fatura
nunca entra nos gastos. Categoria sem orçamento é exibida como "Não
definido", sem assumir zero (DD-10 definida). Indicadores de utilização:
dentro do orçamento, próximo do limite (80% — decisão aprovada na
Fase 7), totalmente utilizado e ultrapassado. Tela de orçamentos com
seleção de mês e cartão, totalizador e criação de compra a partir da
categoria orçada (T-059). Testes: 110 no back-end e 39 no front-end.

## 13. Fase 8 --- Testes, segurança e qualidade

**Objetivo:** verificar cálculos, permissões, usabilidade e
estabilidade.

-   [x] **T-060 \[P0\]** Criar testes unitários para cálculos
    financeiros.
    -   Soma de receitas.
    -   Soma de despesas fixas e variáveis.
    -   Investimentos.
    -   Total de saídas e restante.
    -   Orçamento menos gastos.
    -   Distribuição de parcelas, se aplicável.
-   [x] **T-061 \[P0\]** Criar testes de faturas.
    -   Compra antes do fechamento.
    -   Compra depois do fechamento.
    -   Compra no dia do fechamento.
    -   Meses com 28, 29, 30 e 31 dias.
    -   Virada de ano.
-   [x] **T-062 \[P0\]** Criar testes de autorização.
    -   Usuário não acessa cartão de outro usuário.
    -   Usuário não acessa movimentação de outro usuário.
    -   Usuário não altera orçamento de outro usuário.
    -   Usuário não consulta fatura de outro usuário.
-   [x] **T-063 \[P0\]** Criar testes de integração da API.
    -   Cadastro e autenticação.
    -   Categorias e movimentações.
    -   Dashboard mensal e anual.
    -   Cartões, compras e faturas.
    -   Orçamentos.
-   [x] **T-064 \[P0\]** Criar testes de interface dos fluxos
    essenciais.
    -   Registrar receita.
    -   Registrar despesa.
    -   Navegar entre meses e anos.
    -   Alternar visão mensal/anual.
    -   Cadastrar cartão e compra.
    -   Criar orçamento e verificar restante.
-   [x] **T-065 \[P1\]** Realizar revisão de segurança.
    -   Validar proteção das rotas.
    -   Verificar exposição de dados em logs.
    -   Verificar armazenamento de senhas e tokens.
    -   Verificar configuração de CORS e HTTPS para produção.
-   [x] **T-066 \[P1\]** Realizar revisão de usabilidade e
    acessibilidade.
    -   Navegação por teclado.
    -   Rótulos e mensagens de validação.
    -   Contraste e legibilidade.
    -   Fluxos em telas pequenas.
-   [x] **T-067 \[P1\]** Validar cálculos com exemplos reais da
    planilha.
    -   Selecionar meses com receitas e despesas variadas.
    -   Comparar totais e restante.
    -   Comparar compras, faturas e orçamentos.
    -   Registrar diferenças explicadas por regras definidas.

**Critério de conclusão da fase:** testes essenciais passam e os
cálculos do sistema são reconciliados com exemplos da planilha segundo
as regras aprovadas.

**Fase 8 concluída:** testes ampliados para 159 no back-end e 50 no
front-end. T-060/T-061: cálculos financeiros (receitas, fixas,
variáveis, investimentos, saídas, restante, orçamento − gastos e
precisão decimal sem ponto flutuante) e faturas (antes/depois/no dia do
fechamento, meses de 28/29/30/31 dias, ano bissexto e virada de ano).
T-062/T-063: autorização (nenhum acesso a cartão, movimentação,
orçamento, compra ou fatura alheios; todas as rotas privadas exigem
token) e integração ponta a ponta com consistência após alterações.
T-064: testes de interface dos fluxos essenciais (receita, despesa,
navegação por meses/anos, alternar visão mensal/anual, cartão, compra e
orçamento). T-065 (segurança): rotas protegidas confirmadas; senhas com
bcrypt e tokens de recuperação com hash; erros de validação não refletem
mais os valores enviados (ex.: senhas); produção recusa iniciar com
`SECRET_KEY` de desenvolvimento ou `EMAIL_BACKEND=console`; HTTPS e
CORS restrito são da configuração de produção (T-068/T-069). T-066
(usabilidade/acessibilidade): teclado (Escape fecha modais; foco
movido para o diálogo ao abrir), rótulos associados e mensagens com
`role="alert"`, significados não dependem só de cor, tabelas com
rolagem em telas pequenas; recomendações registradas: focus trap nos
modais e passada manual em telas pequenas (T-043). T-067: reconciliação
com os exemplos oficiais da planilha (`spec.md` §7.4) cobrindo
AC-096 a AC-099 — competência da fatura, ausência de dupla contagem,
resumo do mês (saídas R$ 3.200,00, restante R$ 1.800,00) e orçamento por
ciclo; sem divergências além das já explicadas pelas regras definidas
(AC-100).

## 14. Fase 9 --- Publicação e operação

**Objetivo:** disponibilizar o sistema em ambiente de produção.

-   [ ] **T-068 \[P0\]** Preparar configuração de produção.
    -   Variáveis de ambiente.
    -   Segredos fora do repositório.
    -   Configuração de banco.
    -   Configuração de CORS.
-   [ ] **T-069 \[P0\]** Configurar hospedagem.
    -   Publicar front-end.
    -   Publicar back-end.
    -   Configurar domínio e HTTPS.
    -   Verificar comunicação entre front-end e API.
-   [ ] **T-070 \[P0\]** Configurar migrações e dados iniciais.
    -   Aplicar migrações.
    -   Inserir categorias padrão, se aprovadas.
    -   Não inserir dados financeiros fictícios em contas reais.
-   [ ] **T-071 \[P0\]** Configurar backups.
    -   Definir frequência.
    -   Definir retenção.
    -   Documentar processo de restauração.
    -   Testar recuperação.
-   [ ] **T-072 \[P1\]** Configurar logs e monitoramento.
    -   Registrar falhas técnicas sem expor dados financeiros.
    -   Monitorar disponibilidade da API.
    -   Documentar procedimentos básicos de suporte.
-   [ ] **T-073 \[P0\]** Atualizar documentação de instalação e uso.
    -   Pré-requisitos.
    -   Configuração local.
    -   Execução de testes.
    -   Publicação.
    -   Principais fluxos do sistema.

**Critério de conclusão da fase:** aplicação publicada com HTTPS, banco
configurado, backups documentados e fluxos essenciais validados em
produção.

## 15. Itens fora do MVP

Não implementar nesta primeira entrega, salvo decisão explícita
posterior:

-   Integração Open Finance.
-   Importação automática de extratos bancários.
-   Integração automática com operadoras de cartão.
-   Pagamentos ou transferências bancárias.
-   Aplicativos nativos Android e iOS.
-   Gestão financeira compartilhada entre familiares.
-   Recomendações automatizadas de investimentos.
-   Metas avançadas e relatórios analíticos avançados.
-   Exportação de dados, caso permaneça como funcionalidade futura.

## 16. Ordem recomendada de execução

A ordem abaixo considera dependências técnicas e entrega de valor. As
fases podem ser divididas em sprints menores.

  --------------------------------------------------------------------------
                         Ordem Fase                  Resultado esperado
  ---------------------------- --------------------- -----------------------
                             1 Validação das regras  Regras financeiras
                                                     essenciais definidas.

                             2 Fundação              Projeto executando
                                                     localmente.

                             3 Interface base        Layout e navegação
                                                     prontos.

                             4 Autenticação e dados  Contas e isolamento
                                                     funcionando.

                             5 Categorias e          Cadastro e histórico
                               movimentações         funcionando.

                             6 Visão mensal e anual  Resumos consistentes.

                             7 Cartões e faturas     Múltiplos cartões e
                                                     compras funcionando.

                             8 Orçamentos            Planejado, gasto e
                                                     restante por
                                                     cartão/categoria/mês.

                             9 Qualidade             Testes e revisão de
                                                     segurança concluídos.

                            10 Publicação            MVP disponível na
                                                     internet.
  --------------------------------------------------------------------------

## 17. Definição de pronto (Definition of Done)

Uma tarefa poderá ser considerada concluída quando:

-   [ ] O comportamento descrito foi implementado.
-   [ ] O código segue a organização e os padrões do projeto.
-   [ ] As validações necessárias estão no front-end e no back-end.
-   [ ] Foram adicionados ou atualizados testes pertinentes.
-   [ ] Os testes relacionados foram executados com sucesso.
-   [ ] Não há exposição indevida de dados de outros usuários.
-   [ ] A interface apresenta estados de carregamento, sucesso e erro
    quando aplicável.
-   [ ] A documentação foi atualizada quando necessário.
-   [ ] A tarefa foi revisada e não introduz regressões conhecidas.

## 18. Orientações para desenvolvimento com IA

Ao utilizar uma IA de programação para implementar o meuSaldo:

1.  Ler `requirements.md`, `spec.md`, `design.md` e este `tasks.md`
    antes de iniciar uma tarefa.
2.  Implementar uma tarefa por vez ou um pequeno grupo de tarefas
    diretamente relacionadas.
3.  Não alterar regras de negócio sem autorização.
4.  Não inventar comportamentos para decisões marcadas como pendentes.
5.  Antes de alterar arquivos, identificar a estrutura atual do projeto.
6.  Reutilizar componentes e serviços existentes.
7.  Criar ou atualizar testes junto com a implementação.
8.  Executar os testes e corrigir erros antes de marcar a tarefa como
    concluída.
9.  Atualizar este documento com o status real das tarefas.
10. Ao finalizar cada etapa, informar arquivos alterados, decisões
    tomadas, testes executados e pendências.

**Prompt inicial sugerido para a IA de programação:**

> Leia os documentos da pasta `docs/`, especialmente `requirements.md`,
> `spec.md`, `design.md` e `tasks.md`. Analise a estrutura atual do
> repositório e identifique a primeira tarefa pendente cuja dependência
> esteja atendida. Antes de implementar, explique brevemente o objetivo,
> os arquivos que pretende criar ou alterar e os critérios de conclusão.
> Implemente somente essa tarefa, respeitando as regras documentadas.
> Não invente regras para decisões pendentes. Ao terminar, execute os
> testes pertinentes e informe o resultado. Não marque tarefas como
> concluídas se não tiver verificado seus critérios.

------------------------------------------------------------------------

**Nota:** este plano é incremental. A prioridade é entregar primeiro um
controle financeiro pessoal confiável e simples; funcionalidades
adicionais só deverão ser incorporadas quando não comprometerem essa
experiência.
