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

-   [ ] **T-001 \[P0\]** Revisar os documentos e alinhar nomes e
    decisões do produto.
    -   Confirmar o nome `meuSaldo` em todos os documentos.
    -   Confirmar que a visão geral mensal e anual fazem parte do
        escopo.
    -   Confirmar múltiplos cartões e orçamento por cartão, categoria e
        mês.
    -   Registrar divergências encontradas entre `requirements.md`,
        `spec.md` e `design.md`.
-   [ ] **T-002 \[P0\]** Definir a política de contabilização de
    despesas e compras no cartão.
    -   Determinar qual data define o mês da despesa.
    -   Definir como compras e faturas aparecem na visão mensal e anual.
    -   Garantir que compra e pagamento da fatura não sejam
        contabilizados duas vezes.
    -   Documentar exemplos de cálculo.
-   [ ] **T-003 \[P0\]** Definir a relação entre mês da compra, mês da
    fatura e mês do orçamento.
    -   Decidir se o orçamento considera a data da compra ou o ciclo da
        fatura.
    -   Aplicar a mesma regra na tela de cartões e na tela de
        orçamentos.
-   [ ] **T-004 \[P1\]** Definir regras de fechamento e vencimento das
    faturas.
    -   Definir o tratamento de compras feitas no dia do fechamento.
    -   Definir o cálculo para meses com menos dias que o dia
        configurado.
    -   Definir como será criada a primeira fatura de um cartão.
-   [ ] **T-005 \[P1\]** Decidir se compras parceladas farão parte do
    MVP.
    -   Se aprovadas, definir distribuição de centavos e atribuição das
        parcelas às faturas.
    -   Se não aprovadas, limitar a primeira versão a compras não
        parceladas e registrar parcelamento como evolução.
-   [ ] **T-006 \[P1\]** Definir o cálculo do limite comprometido e
    disponível.
    -   Decidir se parcelas futuras comprometem o limite.
    -   Definir como pagamentos de fatura liberam limite.
-   [ ] **T-007 \[P1\]** Definir o escopo de recorrência de despesas
    fixas.
    -   Decidir se cada mês terá lançamentos manuais ou se haverá
        geração de despesas recorrentes.
    -   Não implementar recorrência automática sem essa decisão.
-   [ ] **T-008 \[P1\]** Definir categorias iniciais e tipos de
    movimentação.
    -   Separar receitas, despesas fixas, despesas variáveis e
        investimentos.
    -   Definir quais categorias padrão serão disponibilizadas.
    -   Definir se o usuário poderá criar, editar, desativar e reativar
        categorias.

**Critério de conclusão da fase:** decisões registradas nos documentos
de especificação e regras necessárias aos cálculos aprovadas.

## 6. Fase 1 --- Fundação do projeto e ambiente

**Objetivo:** preparar a estrutura técnica para o desenvolvimento.

-   [ ] **T-009 \[P0\]** Criar o repositório Git do meuSaldo.
    -   Criar estrutura inicial de pastas.
    -   Adicionar `.gitignore`.
    -   Criar `README.md` com visão geral e instruções iniciais.
-   [ ] **T-010 \[P0\]** Inicializar o back-end com Python e FastAPI.
    -   Criar aplicação principal.
    -   Configurar variáveis de ambiente.
    -   Criar endpoint de verificação de saúde, por exemplo `/health`.
    -   Configurar documentação OpenAPI.
-   [ ] **T-011 \[P0\]** Inicializar o front-end com Vue.js 3.
    -   Configurar Vite.
    -   Configurar Tailwind CSS.
    -   Configurar roteamento.
    -   Criar tela inicial e estrutura de layout.
-   [ ] **T-012 \[P0\]** Configurar PostgreSQL.
    -   Criar banco e usuário de aplicação.
    -   Configurar conexão pelo back-end.
    -   Utilizar variáveis de ambiente para credenciais.
-   [ ] **T-013 \[P0\]** Configurar migrações do banco.
    -   Integrar ferramenta de migração, como Alembic.
    -   Criar primeira migração.
    -   Documentar como aplicar e reverter migrações.
-   [ ] **T-014 \[P1\]** Preparar ambiente local com Docker Compose.
    -   Configurar serviços de front-end, back-end e banco de dados,
        conforme necessário.
    -   Configurar volumes e rede interna.
    -   Documentar comandos para subir e encerrar o ambiente.
-   [ ] **T-015 \[P0\]** Configurar padrões de qualidade.
    -   Definir formatação e lint para Python e JavaScript.
    -   Configurar tratamento padronizado de erros.
    -   Criar configuração inicial de testes automatizados.

**Critério de conclusão da fase:** front-end e back-end iniciam
localmente, conectam ao banco e possuem instruções reproduzíveis.

## 7. Fase 2 --- Identidade visual e estrutura de navegação

**Objetivo:** construir a base visual conforme o protótipo de
referência.

-   [ ] **T-016 \[P0\]** Definir tokens visuais.
    -   Cores principais, neutras, positivas, negativas e de atenção.
    -   Tipografia, espaçamentos, bordas, sombras e raios.
    -   Estados de foco, hover, desabilitado e erro.
-   [ ] **T-017 \[P0\]** Criar layout principal da aplicação.
    -   Implementar marca e nome `meuSaldo`.
    -   Criar navegação lateral para telas grandes.
    -   Criar navegação compacta para dispositivos móveis.
    -   Reservar área de conteúdo principal.
-   [ ] **T-018 \[P0\]** Criar componentes compartilhados.
    -   Botões, campos, seletores, modais e tabelas.
    -   Cartões de indicadores.
    -   Mensagens de sucesso e erro.
    -   Estados de carregamento e listas vazias.
    -   Campo monetário com formatação brasileira.
-   [ ] **T-019 \[P1\]** Criar componentes de período.
    -   Seletor de mês e ano.
    -   Navegação para mês anterior e próximo.
    -   Seletor de ano.
    -   Alternância entre visão mensal e anual.
-   [ ] **T-020 \[P1\]** Validar responsividade do layout.
    -   Testar larguras de desktop, tablet e smartphone.
    -   Garantir navegação e formulários utilizáveis em telas pequenas.

**Critério de conclusão da fase:** layout consistente, navegável e
responsivo, ainda que utilizando dados de demonstração.

## 8. Fase 3 --- Banco de dados, autenticação e isolamento

**Objetivo:** implementar a base de dados e o acesso seguro dos
usuários.

-   [ ] **T-021 \[P0\]** Implementar entidade e migração de usuário.
    -   Nome, e-mail, hash da senha e datas de auditoria.
    -   Garantir unicidade do e-mail.
-   [ ] **T-022 \[P0\]** Implementar cadastro de usuário.
    -   Validar campos.
    -   Validar e-mail único.
    -   Armazenar senha com hash seguro.
-   [ ] **T-023 \[P0\]** Implementar login e logout.
    -   Validar credenciais.
    -   Configurar mecanismo de sessão ou token.
    -   Definir armazenamento e expiração de credenciais.
    -   Implementar encerramento da sessão.
-   [ ] **T-024 \[P0\]** Proteger rotas do front-end e endpoints
    privados.
    -   Redirecionar usuários não autenticados.
    -   Validar autorização no back-end.
-   [ ] **T-025 \[P0\]** Implementar isolamento dos dados por usuário.
    -   Aplicar o usuário autenticado nas consultas.
    -   Impedir acesso a registros de outro usuário por alteração de
        IDs.
    -   Criar testes de autorização.
-   [ ] **T-026 \[P1\]** Implementar recuperação de senha, caso aprovada
    para o MVP.
    -   Definir envio de e-mail.
    -   Criar fluxo seguro de redefinição.
    -   Não revelar se determinado e-mail está cadastrado.

**Critério de conclusão da fase:** usuário consegue criar conta e
acessar áreas privadas; testes comprovam isolamento dos dados.

## 9. Fase 4 --- Categorias e movimentações financeiras

**Objetivo:** permitir registrar e consultar as informações que
alimentam o controle financeiro.

### Categorias

-   [ ] **T-027 \[P0\]** Criar modelo e migrações de categorias.
    -   Suportar categorias padrão e categorias do usuário.
    -   Suportar grupos receita, despesa e investimento.
    -   Suportar classificação fixa ou variável para despesas.
    -   Suportar ativação e desativação.
-   [ ] **T-028 \[P0\]** Implementar API e interface de categorias.
    -   Listar, criar e editar categorias.
    -   Ativar e desativar categorias.
    -   Impedir incompatibilidade entre categoria e tipo de
        movimentação.

### Receitas

-   [ ] **T-029 \[P0\]** Criar modelo e API de receitas.
    -   Descrição, valor, data, categoria e observações.
    -   Validar valor positivo e categoria compatível.
    -   Associar ao usuário autenticado.
-   [ ] **T-030 \[P0\]** Criar formulário e listagem de receitas.
    -   Cadastrar, editar e excluir.
    -   Apresentar mensagens de validação.
    -   Atualizar informações após salvar.

### Despesas

-   [ ] **T-031 \[P0\]** Criar modelo e API de despesas.
    -   Descrição, valor, data, categoria, forma de pagamento e
        observações.
    -   Classificação fixa ou variável.
    -   Validar valor e categoria.
-   [ ] **T-032 \[P0\]** Criar formulário e listagem de despesas.
    -   Cadastrar, editar e excluir.
    -   Exibir forma de pagamento e classificação.
    -   Atualizar informações após salvar.

### Investimentos

-   [ ] **T-033 \[P1\]** Implementar registro de investimentos.
    -   Descrição, valor, data, categoria ou objetivo.
    -   Apresentar investimentos em seção própria.
    -   Considerar investimentos no cálculo do restante conforme regra
        aprovada.

### Histórico

-   [ ] **T-034 \[P0\]** Criar tela de movimentações.
    -   Listar registros por data.
    -   Filtrar por período, tipo, categoria e forma de pagamento.
    -   Oferecer ações de edição e exclusão.
    -   Exibir estado vazio e filtros sem resultado.

**Critério de conclusão da fase:** usuário consegue registrar, editar,
excluir, filtrar e consultar seus registros financeiros com dados
persistidos.

## 10. Fase 5 --- Visão geral mensal e anual

**Objetivo:** transformar a visão principal da planilha em duas
visualizações integradas.

### Visão mensal

-   [ ] **T-035 \[P0\]** Implementar serviço de resumo mensal no
    back-end.
    -   Total de receitas.
    -   Total de despesas fixas.
    -   Total de despesas variáveis.
    -   Total de investimentos.
    -   Total de saídas.
    -   Restante do mês.
    -   Aplicar a política de contabilização aprovada.
-   [ ] **T-036 \[P0\]** Implementar API do dashboard mensal.
    -   Receber mês e ano.
    -   Retornar indicadores e itens agrupados.
    -   Retornar últimas movimentações, se aplicável.
-   [ ] **T-037 \[P0\]** Implementar interface da visão mensal.
    -   Seletor de mês e ano.
    -   Indicadores financeiros.
    -   Seções de contas a receber, despesas fixas, despesas variáveis e
        investimentos.
    -   Resumo do mês.
    -   Acesso rápido para adicionar movimentação.
-   [ ] **T-038 \[P0\]** Implementar navegação entre meses.
    -   Mês anterior.
    -   Próximo mês.
    -   Retorno ao mês atual.
    -   Preservar o contexto ao alternar de visualização.

### Visão anual

-   [ ] **T-039 \[P1\]** Implementar serviço de resumo anual no
    back-end.
    -   Receber ano selecionado.
    -   Calcular os totais de cada mês.
    -   Agrupar receitas, despesas fixas, despesas variáveis e
        investimentos.
    -   Calcular restante de cada mês.
    -   Evitar duplicidade de compras e faturas.
-   [ ] **T-040 \[P1\]** Implementar API do dashboard anual.
    -   Retornar os 12 meses, inclusive meses sem movimentação.
    -   Retornar totais anuais e valores por grupo.
    -   Garantir ordenação cronológica.
-   [ ] **T-041 \[P1\]** Implementar interface da visão anual.
    -   Apresentar meses em colunas.
    -   Apresentar grupos financeiros em linhas.
    -   Exibir totais mensais e anuais.
    -   Permitir selecionar um mês para abrir sua visão mensal.
    -   Permitir navegar entre anos.
-   [ ] **T-042 \[P1\]** Implementar alternância mensal/anual.
    -   Manter o ano selecionado.
    -   Preservar o mês de referência quando fizer sentido.
    -   Exibir claramente qual visualização está ativa.
-   [ ] **T-043 \[P1\]** Validar visão anual em telas menores.
    -   Implementar rolagem horizontal controlada ou apresentação
        compacta.
    -   Evitar truncamento de valores.
    -   Manter os meses identificáveis.

**Critério de conclusão da fase:** os dados da visão mensal e anual são
consistentes entre si; selecionar um mês na visão anual abre o resumo
mensal correspondente.

## 11. Fase 6 --- Múltiplos cartões, compras e faturas

**Objetivo:** implementar o controle de vários cartões de crédito por
usuário.

-   [ ] **T-044 \[P0\]** Criar modelo e migrações de cartões.
    -   Nome, emissor opcional, limite, fechamento, vencimento e
        situação.
    -   Associar cada cartão ao usuário.
    -   Não armazenar número completo, CVV ou senha.
-   [ ] **T-045 \[P0\]** Implementar API e interface de cartões.
    -   Listar, cadastrar, editar e inativar.
    -   Exibir limite e dados básicos.
    -   Impedir compras em cartões inativos.
-   [ ] **T-046 \[P0\]** Criar modelo de compras no cartão.
    -   Cartão, categoria, descrição, data e valor.
    -   Associar compra ao usuário e cartão.
    -   Validar compatibilidade de propriedade dos registros.
-   [ ] **T-047 \[P0\]** Implementar cadastro e histórico de compras.
    -   Registrar compra em cartão selecionado.
    -   Listar compras por cartão e período.
    -   Editar e excluir compras.
    -   Atualizar valores de orçamento relacionados.
-   [ ] **T-048 \[P0\]** Implementar cálculo do ciclo de fatura.
    -   Considerar fechamento e vencimento.
    -   Tratar virada de mês e meses com duração diferente.
    -   Aplicar a regra aprovada para compras no dia do fechamento.
-   [ ] **T-049 \[P0\]** Implementar entidades e API de faturas.
    -   Agrupar compras no ciclo correto.
    -   Calcular total da fatura.
    -   Consultar fatura atual, próxima e histórico.
    -   Evitar duplicidade no resumo financeiro.
-   [ ] **T-050 \[P1\]** Implementar acompanhamento de limite.
    -   Calcular valor comprometido.
    -   Calcular limite disponível.
    -   Aplicar a política aprovada para parcelas e pagamentos.
-   [ ] **T-051 \[P1\]** Implementar pagamento de fatura, se aprovado.
    -   Registrar pagamento total ou parcial.
    -   Tratar pagamento como liquidação da obrigação.
    -   Não criar uma segunda despesa de consumo.
-   [ ] **T-052 \[P1\]** Implementar parcelamento, se aprovado para o
    MVP.
    -   Distribuir parcelas entre faturas.
    -   Garantir soma exata do valor original.
    -   Tratar diferenças de centavos.
    -   Atualizar limite e orçamento conforme regras aprovadas.

**Critério de conclusão da fase:** o usuário consegue gerenciar vários
cartões, registrar compras e consultar faturas; os cálculos não duplicam
despesas.

## 12. Fase 7 --- Orçamentos por cartão e categoria

**Objetivo:** implementar a funcionalidade baseada na segunda planilha
enviada.

-   [ ] **T-053 \[P0\]** Criar modelo e migração de orçamento por
    cartão.
    -   Usuário.
    -   Cartão.
    -   Categoria.
    -   Mês de referência.
    -   Valor planejado.
    -   Restrição de unicidade para usuário + cartão + categoria + mês.
-   [ ] **T-054 \[P0\]** Implementar API de consulta de orçamentos.
    -   Receber mês e cartão.
    -   Listar categorias orçadas.
    -   Retornar valor planejado, gastos e restante.
    -   Retornar categorias sem orçamento como "Não definido", sem
        assumir zero.
-   [ ] **T-055 \[P0\]** Implementar criação, edição e exclusão de
    orçamentos.
    -   Validar cartão e categoria pertencentes ao usuário.
    -   Impedir orçamento duplicado para a mesma combinação.
    -   Validar valores não negativos.
-   [ ] **T-056 \[P0\]** Implementar tela de orçamentos.
    -   Seleção de mês.
    -   Seleção de cartão.
    -   Tabela com categoria, orçamento, gastos e restante.
    -   Totalizador.
    -   Ação para novo orçamento.
-   [ ] **T-057 \[P0\]** Implementar cálculo de gastos por categoria.
    -   Considerar somente compras do cartão e mês conforme política
        aprovada.
    -   Atualizar totais após inclusão, edição ou exclusão de compra.
    -   Evitar somar pagamento de fatura como nova compra.
-   [ ] **T-058 \[P1\]** Implementar indicadores de utilização.
    -   Dentro do orçamento.
    -   Próximo do limite.
    -   Orçamento ultrapassado.
    -   Calcular percentual somente quando houver orçamento maior que
        zero.
    -   Utilizar o percentual de alerta aprovado.
-   [ ] **T-059 \[P1\]** Permitir iniciar compra a partir de uma
    categoria orçada.
    -   Abrir formulário com cartão e categoria preenchidos.
    -   Após salvar, atualizar gastos e restante.

**Critério de conclusão da fase:** para cada cartão e mês, o usuário
consegue definir orçamento por categoria e acompanhar planejado, gasto e
restante corretamente.

## 13. Fase 8 --- Testes, segurança e qualidade

**Objetivo:** verificar cálculos, permissões, usabilidade e
estabilidade.

-   [ ] **T-060 \[P0\]** Criar testes unitários para cálculos
    financeiros.
    -   Soma de receitas.
    -   Soma de despesas fixas e variáveis.
    -   Investimentos.
    -   Total de saídas e restante.
    -   Orçamento menos gastos.
    -   Distribuição de parcelas, se aplicável.
-   [ ] **T-061 \[P0\]** Criar testes de faturas.
    -   Compra antes do fechamento.
    -   Compra depois do fechamento.
    -   Compra no dia do fechamento.
    -   Meses com 28, 29, 30 e 31 dias.
    -   Virada de ano.
-   [ ] **T-062 \[P0\]** Criar testes de autorização.
    -   Usuário não acessa cartão de outro usuário.
    -   Usuário não acessa movimentação de outro usuário.
    -   Usuário não altera orçamento de outro usuário.
    -   Usuário não consulta fatura de outro usuário.
-   [ ] **T-063 \[P0\]** Criar testes de integração da API.
    -   Cadastro e autenticação.
    -   Categorias e movimentações.
    -   Dashboard mensal e anual.
    -   Cartões, compras e faturas.
    -   Orçamentos.
-   [ ] **T-064 \[P0\]** Criar testes de interface dos fluxos
    essenciais.
    -   Registrar receita.
    -   Registrar despesa.
    -   Navegar entre meses e anos.
    -   Alternar visão mensal/anual.
    -   Cadastrar cartão e compra.
    -   Criar orçamento e verificar restante.
-   [ ] **T-065 \[P1\]** Realizar revisão de segurança.
    -   Validar proteção das rotas.
    -   Verificar exposição de dados em logs.
    -   Verificar armazenamento de senhas e tokens.
    -   Verificar configuração de CORS e HTTPS para produção.
-   [ ] **T-066 \[P1\]** Realizar revisão de usabilidade e
    acessibilidade.
    -   Navegação por teclado.
    -   Rótulos e mensagens de validação.
    -   Contraste e legibilidade.
    -   Fluxos em telas pequenas.
-   [ ] **T-067 \[P1\]** Validar cálculos com exemplos reais da
    planilha.
    -   Selecionar meses com receitas e despesas variadas.
    -   Comparar totais e restante.
    -   Comparar compras, faturas e orçamentos.
    -   Registrar diferenças explicadas por regras definidas.

**Critério de conclusão da fase:** testes essenciais passam e os
cálculos do sistema são reconciliados com exemplos da planilha segundo
as regras aprovadas.

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
