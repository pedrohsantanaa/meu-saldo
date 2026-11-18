# design.md --- meuSaldo

**Projeto:** meuSaldo --- Controle Financeiro Pessoal\
**Versão:** 0.2 --- Revisão com visões mensal e anual\
**Documentos de referência:** `requirements.md` e `spec.md`\
**Referência visual e funcional:** planilhas enviadas pelo responsável
pelo produto.

------------------------------------------------------------------------

## 1. Objetivo do documento

Este documento define a proposta inicial de experiência do usuário,
interface, arquitetura, organização dos módulos, modelo de dados e API
do meuSaldo.

O design parte da estrutura utilizada na planilha atual, preservando os
conceitos que já fazem sentido para o usuário:

-   Visão financeira mensal.
-   Receitas organizadas por fonte.
-   Despesas fixas e variáveis.
-   Investimentos apresentados separadamente.
-   Total de receitas, total de despesas e restante do mês.
-   Controle de gastos por cartão.
-   Orçamento mensal por categoria e por cartão.
-   Comparação entre valor orçado, valor gasto e valor restante.

O objetivo não é reproduzir literalmente uma planilha na tela, mas
transformar sua lógica em uma aplicação web simples, responsiva e fácil
de manter.

## 2. Decisões de produto confirmadas

As decisões abaixo foram informadas pelo responsável pelo produto e
deverão orientar a implementação.

  ---------------------------------------------------------------------
  Tema                               Decisão
  ---------------------------------- ----------------------------------
  Cartões de crédito                 O usuário poderá cadastrar e
                                     controlar vários cartões.

  Orçamento                          O orçamento será definido por
                                     categoria e por cartão.

  Visão geral                        A tela principal exibirá um mês
                                     por vez, com navegação entre
                                     meses.
  ---------------------------------------------------------------------

### 2.1. Consequências dessas decisões

-   Cada usuário poderá ter vários cartões, como Nubank, Banco do
    Brasil, Inter e outros.
-   Uma categoria poderá possuir limites diferentes em cartões
    diferentes.
-   O mesmo cartão poderá ter diversos orçamentos de categoria em cada
    mês.
-   O usuário poderá navegar para o mês anterior ou próximo sem perder o
    contexto.
-   A visão mensal será a tela principal do MVP. A visão anual faz parte
    do escopo planejado, como visão comparativa com os 12 meses em
    colunas e alternância entre as duas visualizações (decisão posterior
    do responsável pelo produto, registrada em `tasks.md` e
    `acceptance.md`).

## 3. Princípios de design

1.  **Simplicidade:** mostrar primeiro as informações mais importantes.
2.  **Fidelidade à planilha:** preservar os grupos e conceitos que já
    fazem parte do controle financeiro utilizado.
3.  **Poucos passos:** facilitar o registro de receitas, despesas e
    compras.
4.  **Leitura rápida:** destacar valores e totais sem excesso de
    gráficos.
5.  **Consistência:** utilizar os mesmos padrões de campos, botões,
    tabelas e cores em todas as telas.
6.  **Responsividade:** adaptar a experiência para computador e celular.
7.  **Privacidade:** cada usuário acessa somente seus próprios dados.

## 4. Estrutura de navegação

A navegação principal deverá conter:

  Seção           Objetivo
  --------------- ----------------------------------------------------------
  Visão geral     Consultar o resumo financeiro nas visões mensal e anual.
  Movimentações   Registrar e consultar receitas e despesas.
  Cartões         Gerenciar cartões, compras e faturas.
  Orçamentos      Planejar e acompanhar gastos por categoria e cartão.
  Categorias      Gerenciar categorias de receitas e despesas.
  Configurações   Gerenciar dados e preferências da conta.

A navegação deverá ser enxuta. No computador, poderá ser apresentada em
uma barra lateral. Em telas pequenas, deverá utilizar menu compacto ou
navegação adaptada.

## 5. Design das telas

### 5.1. Visão geral mensal

**Objetivo:** apresentar a situação financeira do mês selecionado,
mantendo a lógica da primeira planilha enviada.

#### Cabeçalho

O cabeçalho deverá apresentar:

-   Nome do produto: meuSaldo.
-   Mês e ano selecionados.
-   Botão para mês anterior.
-   Botão para próximo mês.
-   Ação para retornar ao mês atual.
-   Acesso ao cadastro rápido de movimentação.

Exemplo conceitual:

`<` **Novembro de 2026** `>`\
`[Adicionar movimentação]`

#### Indicadores principais

Na parte superior, exibir quatro indicadores:

1.  **Total de receitas:** soma das receitas do mês.
2.  **Despesas fixas:** soma das despesas classificadas como fixas.
3.  **Despesas variáveis:** soma das despesas variáveis, incluindo os
    valores de faturas conforme a política de contabilização aprovada.
4.  **Restante:** resultado entre receitas e saídas consideradas no mês.

O total de investimentos deverá permanecer visível em uma seção própria
e também ser considerado no cálculo do restante, seguindo a estrutura da
planilha atual.

#### Organização do conteúdo

A visão geral deverá manter cinco grupos:

**A. Contas a receber**

Lista de fontes de receita, como:

-   Salário Senac.
-   FaSeC.
-   Salário IF.
-   Férias.
-   Agência Fomento.
-   Extras.

Os nomes acima são exemplos observados na planilha. O sistema deverá
permitir que o usuário personalize suas fontes e categorias.

Cada linha deverá mostrar a descrição e o valor do mês selecionado.

**B. Contas a pagar --- Fixas**

Exemplos observados:

-   Aluguel.
-   Condomínio.
-   Água e energia.
-   Plano de saúde.
-   Plano odontológico.
-   Academia.
-   Proteção veicular.
-   Recarga de celular/internet.
-   Parcela de carro.

**C. Contas a pagar --- Variáveis**

Exemplos observados:

-   Fatura de cartão Nubank.
-   Fatura de cartão Banco do Brasil.
-   Fatura de cartão Inter.
-   Almoço.
-   Lanches.
-   Extras.
-   Cabelo.
-   Plano de saúde.
-   Diarista.
-   Gasolina.

As categorias e contas deverão ser configuráveis. Os cartões cadastrados
pelo usuário poderão aparecer como itens de fatura, sem depender de
nomes fixos no código.

**D. Investimentos**

Exemplos observados:

-   Poupança.
-   Mês de janeiro ou outros objetivos/reservas.
-   Pagamento destinado a objetivos financeiros.

A seção deverá manter os investimentos separados das despesas de
consumo, mas incluí-los nas saídas consideradas para calcular o restante
do mês, conforme a lógica atual da planilha.

**E. Resumo do mês**

Apresentar:

-   Total de receitas.
-   Total de despesas fixas.
-   Total de despesas variáveis.
-   Total de investimentos.
-   Total de saídas.
-   Restante do mês.

Fórmulas conceituais:

`Total de saídas = Despesas fixas + Despesas variáveis + Investimentos`

`Restante = Total de receitas - Total de saídas`

A tela deverá deixar claro que "restante" é o resultado dos lançamentos
registrados no sistema, e não necessariamente o saldo bancário real.

#### Interações

-   Selecionar um mês diferente.
-   Adicionar uma receita ou despesa.
-   Editar um lançamento.
-   Consultar os detalhes de uma linha.
-   Acessar o cartão relacionado a uma fatura, quando aplicável.
-   Consultar o histórico do item.

#### Comportamento em dispositivos móveis

Em telas pequenas, não utilizar uma tabela anual com muitas colunas. A
visão mensal deverá ser apresentada em cartões ou listas agrupadas por
seção, mantendo os totais em destaque.

### 5.2. Movimentações

**Objetivo:** centralizar o cadastro e a consulta de receitas, despesas
e investimentos.

A tela deverá apresentar:

-   Botão de nova movimentação.
-   Filtro por mês ou intervalo de datas.
-   Filtro por tipo.
-   Filtro por categoria.
-   Filtro por forma de pagamento.
-   Lista de movimentações.

#### Formulário de movimentação

Campos gerais:

-   Tipo: receita, despesa ou investimento.
-   Descrição.
-   Valor.
-   Data.
-   Categoria.
-   Observações, opcionais.

Campos condicionais:

-   Para despesas: tipo de despesa (fixa ou variável) e forma de
    pagamento.
-   Para compras no cartão: cartão utilizado e dados da compra.
-   Para investimentos: objetivo ou categoria de investimento, se
    aplicável.

O formulário deverá exibir somente os campos necessários ao tipo
selecionado.

**Atenção:** uma compra lançada como compra de cartão não deverá ser
cadastrada novamente como uma despesa independente na visão geral. A
aplicação deverá manter uma relação entre a compra e a fatura, evitando
duplicidade.

### 5.3. Cartões

**Objetivo:** permitir que o usuário gerencie vários cartões e acompanhe
as compras e faturas de cada um.

#### Lista de cartões

Cada cartão deverá apresentar:

-   Nome do cartão.
-   Instituição ou emissor, opcional.
-   Limite total.
-   Valor comprometido, conforme regra aprovada.
-   Limite disponível, conforme regra aprovada.
-   Dia de fechamento.
-   Dia de vencimento.
-   Situação: ativo ou inativo.

A tela deverá permitir cadastrar, editar, visualizar e inativar cartões.

Não solicitar nem armazenar número completo do cartão, CVV, senha ou
credenciais bancárias.

#### Detalhes do cartão

Ao selecionar um cartão, apresentar:

-   Identificação do cartão.
-   Limite total e limite disponível.
-   Fatura atual.
-   Próxima fatura, quando houver dados.
-   Compras registradas.
-   Histórico de faturas.
-   Acesso aos orçamentos daquele cartão.

#### Cadastro de compra

Campos:

-   Data da compra.
-   Descrição.
-   Categoria.
-   Valor.
-   Quantidade de parcelas: não aplicável no MVP (sem parcelamento;
    decisão T-005).
-   Observações, opcionais.

A compra deverá ser associada automaticamente ao usuário e ao cartão
selecionado.

### 5.4. Orçamentos por cartão

**Objetivo:** reproduzir a segunda planilha enviada, na qual o usuário
define um orçamento mensal por categoria para cada cartão e acompanha os
gastos realizados.

Esta é uma funcionalidade central do meuSaldo.

#### Seleção de contexto

A tela deverá permitir selecionar:

-   Mês e ano.
-   Cartão.

O orçamento será individual para a combinação:

`Usuário + Cartão + Mês + Categoria`

#### Tabela de orçamento

Colunas:

  Categoria      Orçamento       Gastos     Restante
  ----------- ------------ ------------ ------------
  Gasolina      R\$ 500,00   R\$ 320,00   R\$ 180,00
  Lanche        R\$ 600,00   R\$ 450,00   R\$ 150,00
  Barbeiro      R\$ 300,00   R\$ 150,00   R\$ 150,00

Valores acima são apenas ilustrativos.

Fórmula:

`Restante da categoria = Orçamento - Gastos`

#### Regras de apresentação

-   Se o restante for positivo, exibir o valor ainda disponível.
-   Se o restante for zero, indicar orçamento totalmente utilizado.
-   Se o restante for negativo, indicar que o orçamento foi
    ultrapassado.
-   Quando não houver orçamento definido, apresentar "Não definido" em
    vez de assumir que o limite é zero.
-   Quando não houver gastos, apresentar R\$ 0,00.
-   O total deverá somar os orçamentos, gastos e valores restantes das
    categorias exibidas.
-   A tela deverá permitir incluir, editar e remover orçamentos.
-   O usuário deverá conseguir adicionar uma compra diretamente a partir
    da categoria, se isso facilitar o fluxo.

#### Indicadores visuais

Utilizar indicadores discretos:

-   Dentro do orçamento.
-   Próximo do limite.
-   Orçamento ultrapassado.

O percentual de utilização poderá ser calculado por:

`Percentual utilizado = (Gastos / Orçamento) × 100`

Quando o orçamento for zero ou não estiver definido, não calcular
percentual. Exibir um estado apropriado.

**Pendente de definição:** estabelecer qual percentual caracteriza
"próximo do limite". Sugestão inicial: 80%, configurável futuramente.

### 5.5. Categorias

A tela deverá permitir criar e gerenciar categorias utilizadas em
receitas, despesas, investimentos e orçamentos.

Campos:

-   Nome.
-   Grupo: receita, despesa ou investimento.
-   Tipo de despesa: fixa ou variável, quando aplicável.
-   Cor ou ícone, opcionais.
-   Situação: ativa ou inativa.

As categorias utilizadas em registros antigos não deverão ser excluídas
de forma que comprometa o histórico.

### 5.6. Configurações

A tela deverá permitir:

-   Atualizar nome e dados básicos da conta.
-   Alterar senha.
-   Configurar preferências simples, quando implementadas.
-   Encerrar sessão.

## 6. Identidade visual e componentes

### 6.1. Direção visual

A planilha utiliza cores para diferenciar grupos e destacar totais. A
aplicação deverá preservar a função sem reproduzir necessariamente o
aspecto de células coloridas.

Direção proposta:

-   Fundo neutro e claro.
-   Superfícies brancas ou levemente diferenciadas.
-   Texto em tom escuro e legível.
-   Uma cor principal para ações e navegação.
-   Verde para valores positivos e receitas.
-   Vermelho ou tom de alerta para despesas e orçamento ultrapassado.
-   Amarelo ou âmbar para atenção e proximidade do limite.
-   Tons distintos e discretos para separar as seções.

As cores deverão ser aplicadas com moderação. O significado nunca deverá
depender apenas da cor: utilizar rótulos, ícones ou textos de apoio.

### 6.2. Componentes reutilizáveis

-   `AppLayout`: estrutura principal da aplicação.
-   `SidebarNavigation`: navegação lateral em telas grandes.
-   `MobileNavigation`: navegação adaptada para celular.
-   `MonthSelector`: seleção e navegação entre meses.
-   `SummaryCard`: indicador financeiro.
-   `SectionHeader`: título de seção e ações.
-   `TransactionForm`: formulário de movimentação.
-   `TransactionList`: lista de movimentações.
-   `CategoryBadge`: identificação de categoria.
-   `CardSummary`: resumo de cartão.
-   `BudgetTable`: tabela de orçamento por categoria.
-   `BudgetStatus`: indicador de utilização do orçamento.
-   `CurrencyInput`: entrada de valores monetários.
-   `EmptyState`: estado sem registros.
-   `ConfirmDialog`: confirmação de operações destrutivas.

Os nomes são sugestões de componentes; a implementação poderá ajustá-los
conforme a organização do front-end.

## 7. Fluxos principais de uso

### 7.1. Registrar receita

1.  Usuário acessa Movimentações ou Visão geral.
2.  Seleciona "Adicionar movimentação".
3.  Seleciona "Receita".
4.  Preenche descrição, valor, data e categoria.
5.  Salva.
6.  O sistema atualiza histórico e indicadores do mês correspondente.

### 7.2. Registrar despesa comum

1.  Usuário seleciona "Adicionar movimentação".
2.  Seleciona "Despesa".
3.  Informa descrição, valor, data, categoria, classificação
    fixa/variável e forma de pagamento.
4.  Salva.
5.  O sistema atualiza a seção correspondente da visão geral.

### 7.3. Registrar compra no cartão

1.  Usuário acessa Cartões.
2.  Seleciona um cartão.
3.  Seleciona "Adicionar compra".
4.  Informa data, descrição, categoria e valor.
5.  Salva.
6.  O sistema associa a compra ao cartão e ao ciclo de fatura
    correspondente.
7.  O sistema atualiza o orçamento da categoria daquele cartão e mês.
8.  O sistema atualiza os valores de cartão e fatura sem duplicar a
    despesa na visão geral.

### 7.4. Definir orçamento por categoria

1.  Usuário acessa Orçamentos.
2.  Seleciona mês e cartão.
3.  Adiciona uma categoria.
4.  Informa o valor planejado.
5.  Salva.
6.  O sistema calcula o total já gasto naquela categoria e apresenta o
    restante.

### 7.5. Consultar visão geral mensal

1.  Usuário acessa Visão geral.
2.  O sistema apresenta o mês atual por padrão.
3.  Usuário navega para mês anterior ou próximo.
4.  O sistema carrega receitas, despesas fixas, despesas variáveis,
    investimentos e resumo do mês selecionado.

## 8. Arquitetura da solução

### 8.1. Arquitetura proposta

Aplicação cliente-servidor, com front-end separado do back-end e
comunicação por API REST.

-   **Front-end:** Vue.js 3.
-   **Estilização:** Tailwind CSS.
-   **Back-end:** Python com FastAPI.
-   **Banco de dados:** PostgreSQL.
-   **Autenticação:** mecanismo baseado em tokens, com estratégia de
    armazenamento e renovação definida na implementação.
-   **Versionamento:** Git e GitHub.
-   **Hospedagem:** VPS ou plataforma cloud.

### 8.2. Responsabilidades

**Front-end**

-   Apresentar telas e componentes.
-   Gerenciar navegação e estado visual.
-   Validar campos para melhorar a experiência.
-   Consumir a API.
-   Exibir erros, carregamentos e confirmações.

**Back-end**

-   Autenticar e autorizar usuários.
-   Validar dados.
-   Aplicar regras de negócio.
-   Calcular totais, saldos, faturas e orçamentos.
-   Garantir isolamento dos dados por usuário.
-   Persistir e consultar dados.

**Banco de dados**

-   Armazenar usuários, categorias, movimentações, cartões, faturas e
    orçamentos.
-   Garantir relacionamentos e integridade dos registros.
-   Armazenar valores monetários com precisão decimal.

## 9. Modelo de dados inicial

O modelo abaixo é conceitual. O detalhamento de tipos, índices,
restrições e migrações deverá ocorrer durante a implementação.

### 9.1. Entidades principais

**User**

-   id
-   name
-   email
-   password_hash
-   created_at
-   updated_at

**Category**

-   id
-   user_id (opcional para categorias padrão globais)
-   name
-   group_type (income, expense, investment)
-   expense_type (fixed, variable, quando aplicável)
-   color
-   icon
-   is_active
-   created_at
-   updated_at

**Transaction**

Representa receitas, despesas comuns e investimentos.

-   id
-   user_id
-   category_id
-   type (income, expense, investment)
-   expense_type (fixed, variable, quando aplicável)
-   description
-   amount
-   transaction_date
-   payment_method
-   notes
-   created_at
-   updated_at

Compras no cartão deverão possuir entidade própria ou relacionamento
explícito com a movimentação, conforme a decisão de modelagem final. Não
deverão ser gravadas duas vezes como despesas independentes.

**CreditCard**

-   id
-   user_id
-   name
-   issuer
-   credit_limit
-   closing_day
-   due_day
-   is_active
-   created_at
-   updated_at

**CreditCardPurchase**

-   id
-   user_id
-   credit_card_id
-   category_id
-   description
-   purchase_date
-   total_amount
-   installments_count
-   notes
-   created_at
-   updated_at

**CreditCardInvoice**

-   id
-   user_id
-   credit_card_id
-   reference_month
-   closing_date
-   due_date
-   status
-   created_at
-   updated_at

**CreditCardInstallment**

Não será utilizada no MVP (sem parcelamento; decisão T-005). Fica
prevista para a evolução com compras parceladas.

-   id
-   purchase_id
-   invoice_id
-   installment_number
-   amount
-   status

**CardCategoryBudget**

-   id
-   user_id
-   credit_card_id
-   category_id
-   reference_month
-   budget_amount
-   created_at
-   updated_at

A combinação usuário, cartão, categoria e mês deverá ser única, evitando
dois orçamentos concorrentes para o mesmo contexto.

### 9.2. Relacionamentos conceituais

-   Um usuário possui várias categorias.
-   Um usuário possui várias movimentações.
-   Um usuário possui vários cartões.
-   Um cartão possui várias compras.
-   Um cartão possui várias faturas.
-   Uma fatura reúne compras ou parcelas.
-   Um cartão possui vários orçamentos mensais.
-   Cada orçamento pertence a uma categoria e a um mês.
-   Uma categoria pode ser utilizada em várias movimentações e
    orçamentos.

### 9.3. Regras de integridade

-   Todo registro privado deverá estar associado a um usuário.
-   O back-end deverá verificar se cartão, categoria, fatura e
    movimentação pertencem ao mesmo usuário.
-   Valores monetários deverão utilizar tipo decimal apropriado.
-   A combinação de cartão, categoria e mês deverá ser única por usuário
    no orçamento.
-   Exclusões deverão respeitar relacionamentos e preservar histórico
    quando necessário.
-   Categorias inativas poderão continuar vinculadas a registros
    antigos.

## 10. API inicial proposta

Os caminhos abaixo são sugestões para orientar o desenho técnico e
poderão ser ajustados.

  -----------------------------------------------------------------------------
  Método             Endpoint                                Responsabilidade
  ------------------ --------------------------------------- ------------------
  POST               `/auth/register`                        Criar usuário.

  POST               `/auth/login`                           Autenticar
                                                             usuário.

  POST               `/auth/logout`                          Encerrar sessão,
                                                             conforme
                                                             estratégia
                                                             adotada.

  GET                `/dashboard?month=YYYY-MM`              Obter resumo
                                                             mensal.

  GET                `/transactions`                         Listar
                                                             movimentações com
                                                             filtros.

  POST               `/transactions`                         Criar movimentação
                                                             comum.

  GET                `/transactions/{id}`                    Consultar
                                                             movimentação.

  PUT                `/transactions/{id}`                    Atualizar
                                                             movimentação.

  DELETE             `/transactions/{id}`                    Excluir
                                                             movimentação.

  GET                `/categories`                           Listar categorias.

  POST               `/categories`                           Criar categoria.

  PUT                `/categories/{id}`                      Atualizar
                                                             categoria.

  PATCH              `/categories/{id}/status`               Ativar ou inativar
                                                             categoria.

  GET                `/cards`                                Listar cartões.

  POST               `/cards`                                Cadastrar cartão.

  GET                `/cards/{id}`                           Consultar cartão.

  PUT                `/cards/{id}`                           Atualizar cartão.

  GET                `/cards/{id}/purchases`                 Listar compras do
                                                             cartão.

  POST               `/cards/{id}/purchases`                 Registrar compra.

  GET                `/cards/{id}/invoices`                  Listar faturas.

  GET                `/budgets?month=YYYY-MM&card_id={id}`   Consultar
                                                             orçamentos do
                                                             cartão no mês.

  POST               `/budgets`                              Criar orçamento
                                                             por categoria e
                                                             cartão.

  PUT                `/budgets/{id}`                         Atualizar
                                                             orçamento.

  DELETE             `/budgets/{id}`                         Remover orçamento.
  -----------------------------------------------------------------------------

Todas as rotas privadas deverão aplicar autenticação, autorização e
isolamento dos dados por usuário.

## 11. Regras de cálculo e consistência

### 11.1. Resumo mensal

A visão geral deverá calcular:

`Total de receitas = soma das receitas do mês`

`Total de despesas fixas = soma das despesas fixas do mês`

`Total de despesas variáveis = soma das despesas variáveis consideradas no mês`

`Total de investimentos = soma dos investimentos do mês`

`Total de saídas = despesas fixas + despesas variáveis + investimentos`

`Restante = receitas - total de saídas`

### 11.2. Orçamento por cartão

Para cada combinação de cartão, mês e categoria:

`Gastos = soma das compras atribuídas ao contexto do orçamento`

`Restante = orçamento - gastos`

A atribuição ao mês segue a política de contabilização definida em
T-002 (`spec.md` §7.2): os gastos do mês são as compras atribuídas ao
ciclo da fatura com vencimento naquele mês. A mesma regra vale para a
tela de orçamento, as faturas e os relatórios.

### 11.3. Prevenção de dupla contagem

A planilha apresenta faturas de cartão na visão geral e detalha compras
por categoria em outra área. O sistema deverá manter essa separação sem
somar a compra individual e o total da fatura como duas despesas
diferentes.

**Proposta de comportamento:**

-   As compras individuais formam o detalhamento da fatura.
-   A fatura representa o total consolidado dessas compras.
-   A visão geral considera o valor da fatura ou a política de
    competência escolhida, uma única vez.
-   O pagamento da fatura deverá ser tratado como liquidação da
    obrigação, e não como nova despesa de consumo.

A política final de datas e contabilização foi definida em T-002 e está
registrada em `spec.md` §7.2.

## 12. Responsividade

### Computador

-   Navegação lateral.
-   Indicadores em linha.
-   Tabelas para movimentações e orçamentos.
-   Formulários em modal ou painel lateral, quando adequado.
-   Conteúdo central com largura confortável para leitura.

### Tablet

-   Navegação compacta.
-   Indicadores em grade.
-   Tabelas adaptadas ou com rolagem horizontal controlada.

### Smartphone

-   Navegação compacta.
-   Indicadores empilhados ou em grade pequena.
-   Listas e cartões em vez de tabelas largas.
-   Formulários em tela ou painel adequado ao dispositivo.
-   Botões de ação acessíveis sem exigir precisão excessiva.

## 13. Estados da interface

As telas deverão prever:

-   Carregamento.
-   Sucesso após salvar.
-   Erro de validação.
-   Erro de comunicação com a API.
-   Lista sem registros.
-   Filtro sem resultados.
-   Categoria sem orçamento definido.
-   Orçamento ultrapassado.
-   Cartão inativo.
-   Mês sem movimentações.

As mensagens deverão ser objetivas e indicar, sempre que possível, como
resolver o problema.

## 14. Segurança e privacidade

-   A API deverá validar autenticação e autorização em todas as
    operações privadas.
-   O usuário só poderá consultar ou alterar dados de sua propriedade.
-   Senhas deverão ser armazenadas com hash apropriado.
-   A aplicação deverá utilizar HTTPS em produção.
-   Segredos deverão ficar fora do código-fonte.
-   Logs não deverão registrar senhas, tokens ou detalhes financeiros
    desnecessários.
-   O sistema não deverá armazenar dados sensíveis do cartão, como
    número completo ou CVV.
-   Deverá existir rotina de backup e recuperação do banco de dados.

## 15. Decisões ainda pendentes

As seguintes decisões afetam a implementação e precisam ser confirmadas:

  -----------------------------------------------------------------------
  ID                      Tema                    Decisão necessária
  ----------------------- ----------------------- -----------------------
  DD-01                   Parcelamento            Compras parceladas
                                                  entram no MVP ou em
                                                  versão futura?

  DD-02                   Orçamento               Os gastos serão
                                                  associados ao mês da
                                                  compra ou ao mês da
                                                  fatura?

  DD-03                   Fatura                  Como tratar compras
                                                  realizadas exatamente
                                                  no dia do fechamento?

  DD-04                   Limite                  O limite comprometido
                                                  considera parcelas
                                                  futuras?

  DD-05                   Pagamento               O usuário poderá
                                                  registrar pagamento
                                                  total ou parcial da
                                                  fatura?

  DD-06                   Saldo                   O restante mensal
                                                  representa resultado
                                                  dos lançamentos ou
                                                  saldo de caixa
                                                  efetivamente
                                                  disponível?

  DD-07                   Categorias              Quais categorias padrão
                                                  serão disponibilizadas
                                                  inicialmente?

  DD-08                   Despesas fixas          O sistema terá
                                                  recorrência automática
                                                  ou o usuário lançará
                                                  cada mês manualmente?

  DD-09                   Investimentos           Investimentos serão
                                                  lançamentos manuais
                                                  simples ou terão
                                                  objetivos e
                                                  acompanhamento
                                                  próprios?

  DD-10                   Orçamento sem valor     Um orçamento não
                                                  cadastrado será exibido
                                                  como "Não definido",
                                                  sem assumir valor zero?
  -----------------------------------------------------------------------

**Nota (T-002):** a decisão DD-02 foi definida: os gastos seguem o ciclo
da fatura, atribuídos ao mês do vencimento da fatura, conforme `spec.md`
§7.2. As demais decisões seguem pendentes.

**Nota (T-004 a T-008):** também foram definidas as decisões DD-01
(sem parcelamento no MVP), DD-03 (compras no dia do fechamento entram no
ciclo seguinte; meses curtos usam o último dia do mês; primeira fatura
inicia no cadastro do cartão), DD-04 (parcelas futuras comprometem o
limite quando existirem), DD-05 (pagamento total ou parcial da fatura é
registrado como liquidação e libera limite), DD-06 (o restante é o
resultado dos lançamentos registrados, não o saldo bancário --- seção
5.1), DD-07 (categorias padrão totalmente editáveis; lista em
`spec.md` §6.3) e DD-08 (despesas fixas com lançamento manual mensal,
sem recorrência automática no MVP). Seguem pendentes: DD-09 e DD-10.

## 16. Estratégia de implementação

Sugestão de sequência:

1.  Configurar estrutura do projeto e ambiente de desenvolvimento.
2.  Implementar autenticação e isolamento dos dados.
3.  Implementar categorias e movimentações.
4.  Implementar visão geral mensal e cálculos.
5.  Implementar cadastro e gerenciamento de múltiplos cartões.
6.  Implementar compras e faturas.
7.  Implementar orçamentos por cartão, categoria e mês.
8.  Implementar responsividade, acessibilidade e estados de interface.
9.  Executar testes funcionais, de segurança e de consistência
    financeira.
10. Preparar publicação e backups.

## 17. Relação com os demais documentos

  ---------------------------------------------------------------------
  Documento                          Responsabilidade
  ---------------------------------- ----------------------------------
  `requirements.md`                  Problema, objetivo, público-alvo,
                                     escopo e requisitos gerais.

  `spec.md`                          Comportamento das funcionalidades
                                     e regras de negócio.

  `design.md`                        Interface, experiência,
                                     arquitetura, modelo de dados e
                                     API.

  `tasks.md`                         Divisão do desenvolvimento em
                                     tarefas menores.

  `acceptance.md`                    Cenários e critérios de validação
                                     do produto.
  ---------------------------------------------------------------------

------------------------------------------------------------------------

**Nota:** este documento é uma proposta inicial de design. As decisões
pendentes deverão ser confirmadas antes da implementação das regras
correspondentes. A planilha enviada é a referência funcional do produto;
a interface web deverá preservar sua lógica principal, mas com navegação
e apresentação adaptadas ao uso em navegador.
