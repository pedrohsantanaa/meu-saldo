# acceptance.md --- meuSaldo

**Projeto:** meuSaldo --- Controle Financeiro Pessoal\
**Versão:** 0.1 --- Critérios de aceitação do MVP\
**Documentos de referência:** `requirements.md`, `spec.md`, `design.md`
e `tasks.md`

------------------------------------------------------------------------

## 1. Objetivo

Este documento define como verificar se as funcionalidades do meuSaldo
foram implementadas corretamente e se o MVP atende aos requisitos do
produto.

Os critérios estão organizados por funcionalidade e acompanhados de
cenários de teste. Eles devem orientar os testes manuais, automatizados,
de integração e de validação com o responsável pelo produto.

Um recurso somente será considerado aceito quando:

-   O comportamento esperado estiver implementado.
-   Os critérios aplicáveis desta documentação forem atendidos.
-   Os testes pertinentes forem executados com sucesso.
-   Não houver falhas conhecidas que comprometam cálculos financeiros,
    privacidade ou integridade dos dados.

## 2. Decisões de produto consideradas

Este documento considera as decisões confirmadas mais recentes:

-   O nome do produto é **meuSaldo**.
-   A aplicação será web e responsiva.
-   O usuário poderá cadastrar e controlar múltiplos cartões.
-   O orçamento será definido por **cartão + categoria + mês**.
-   A visão geral terá duas visualizações: **mensal e anual**.
-   A visão mensal exibirá os detalhes de um mês, com navegação entre
    meses.
-   A visão anual apresentará os 12 meses em colunas para comparação.
-   A experiência deverá preservar a lógica da planilha de referência e
    seguir o protótipo visual aprovado.

**Observação sobre os documentos:** caso algum trecho anterior de
`design.md` ainda descreva somente a visão mensal ou trate a visão anual
como futura, deverá prevalecer a decisão posterior do responsável pelo
produto e a definição registrada em `tasks.md`: as duas visualizações
fazem parte do escopo planejado.

## 3. Convenções de teste

### 3.1. Estrutura dos cenários

Os cenários utilizam o formato:

-   **Dado:** contexto inicial.
-   **Quando:** ação executada.
-   **Então:** resultado esperado.

### 3.2. Prioridade

  -----------------------------------------------------------------------
  Prioridade                          Significado
  ----------------------------------- -----------------------------------
  P0                                  Bloqueia a aceitação do MVP se não
                                      for atendido.

  P1                                  Importante para a experiência
                                      principal; deve ser atendido antes
                                      da validação final, salvo aprovação
                                      explícita.

  P2                                  Melhoria ou evolução posterior.
  -----------------------------------------------------------------------

### 3.3. Resultado dos testes

Para cada cenário, registrar:

-   [ ] Não executado.
-   [ ] Aprovado.
-   [ ] Reprovado.
-   [ ] Bloqueado por decisão pendente.

A aprovação de um cenário deve estar apoiada em evidência, como
resultado de teste automatizado, captura de tela, registro de execução
ou demonstração reproduzível.

## 4. Cadastro, autenticação e privacidade

### AC-001 --- Cadastro de usuário \[P0\]

**Dado** que uma pessoa ainda não possui conta e informa nome, e-mail
válido e senha que atende à política definida,\
**quando** enviar o formulário de cadastro,\
**então** o sistema deverá criar a conta e apresentar uma confirmação
clara.

### AC-002 --- E-mail já cadastrado \[P0\]

**Dado** que o e-mail informado já pertence a uma conta,\
**quando** a pessoa tentar realizar novo cadastro,\
**então** o sistema deverá rejeitar a operação e informar que não foi
possível concluir o cadastro por duplicidade, sem expor dados
particulares da conta existente.

### AC-003 --- Dados inválidos no cadastro \[P0\]

**Dado** que um ou mais campos obrigatórios estejam ausentes ou
inválidos,\
**quando** o formulário for enviado,\
**então** a conta não deverá ser criada e o sistema deverá indicar os
campos que precisam de correção.

### AC-004 --- Senha não armazenada em texto puro \[P0\]

**Dado** que uma conta foi criada,\
**quando** os dados forem consultados no banco,\
**então** a senha não deverá estar armazenada em texto puro.

### AC-005 --- Login válido \[P0\]

**Dado** que o usuário possui credenciais válidas,\
**quando** informar e-mail e senha corretos,\
**então** deverá conseguir acessar as áreas privadas do sistema.

### AC-006 --- Login inválido \[P0\]

**Dado** que o usuário informe credenciais incorretas,\
**quando** tentar entrar,\
**então** o acesso deverá ser negado e a mensagem não deverá revelar se
o e-mail existe ou não.

### AC-007 --- Proteção de rotas \[P0\]

**Dado** que uma pessoa não está autenticada,\
**quando** tentar abrir uma tela privada ou consultar diretamente um
endpoint privado,\
**então** o sistema deverá impedir o acesso.

### AC-008 --- Logout \[P0\]

**Dado** que o usuário está autenticado,\
**quando** encerrar a sessão,\
**então** as operações protegidas não deverão continuar autorizadas pela
sessão encerrada.

### AC-009 --- Isolamento de dados entre usuários \[P0\]

**Dado** que existem dois usuários com registros financeiros
diferentes,\
**quando** um deles tentar consultar, editar ou excluir um registro do
outro, inclusive alterando o identificador enviado à API,\
**então** a operação deverá ser negada e nenhum dado do outro usuário
deverá ser revelado ou alterado.

### AC-010 --- Privacidade no perfil administrativo \[P1\]

**Dado** que existe um usuário com perfil administrativo,\
**quando** acessar recursos de administração,\
**então** deverá conseguir executar somente as operações administrativas
autorizadas, sem acesso automático às descrições, valores ou
movimentações financeiras particulares dos usuários.

## 5. Categorias

### AC-011 --- Criar categoria \[P0\]

**Dado** que o usuário está autenticado e informa nome e grupo válidos
para uma categoria,\
**quando** salvar,\
**então** a categoria deverá ser criada e disponibilizada nos
formulários compatíveis.

### AC-012 --- Categoria incompatível \[P0\]

**Dado** que uma categoria pertence ao grupo de receitas,\
**quando** o usuário tentar utilizá-la em uma despesa,\
**então** o sistema deverá impedir o vínculo.

### AC-013 --- Nome duplicado \[P1\]

**Dado** que o usuário já possui uma categoria com o mesmo nome e tipo,\
**quando** tentar cadastrar outra equivalente,\
**então** o sistema deverá impedir a duplicidade conforme a regra
definida para categorias.

### AC-014 --- Desativar categoria utilizada \[P0\]

**Dado** que uma categoria está vinculada a movimentações existentes,\
**quando** o usuário desativá-la,\
**então** os registros antigos deverão permanecer íntegros e
consultáveis, e a categoria não deverá ser oferecida para novos
lançamentos quando estiver inativa.

## 6. Receitas

### AC-015 --- Registrar receita válida \[P0\]

**Dado** que o usuário informa descrição, valor maior que zero, data e
categoria do tipo receita,\
**quando** salvar,\
**então** a receita deverá ser persistida, associada ao usuário e
exibida no histórico.

### AC-016 --- Validar receita \[P0\]

**Dado** que a receita possui descrição, valor, data ou categoria
ausente, ou valor menor ou igual a zero,\
**quando** o usuário tentar salvar,\
**então** o sistema deverá rejeitar o registro e indicar a correção
necessária.

### AC-017 --- Atualizar total após receita \[P0\]

**Dado** que o usuário está consultando o resumo do período de uma
receita,\
**quando** cadastrar uma nova receita válida nesse período,\
**então** o total de receitas e o restante deverão ser recalculados.

### AC-018 --- Editar receita \[P0\]

**Dado** que existe uma receita cadastrada,\
**quando** o usuário alterar valor, data ou categoria e salvar,\
**então** o histórico e os resumos dos períodos afetados deverão
refletir os novos dados.

### AC-019 --- Excluir receita \[P0\]

**Dado** que existe uma receita cadastrada,\
**quando** o usuário confirmar sua exclusão,\
**então** o registro deverá deixar de compor o histórico e os totais
deverão ser recalculados.

## 7. Despesas e investimentos

### AC-020 --- Registrar despesa válida \[P0\]

**Dado** que o usuário informa descrição, valor maior que zero, data,
categoria do tipo despesa e forma de pagamento,\
**quando** salvar,\
**então** a despesa deverá ser persistida e exibida no histórico.

### AC-021 --- Validar despesa \[P0\]

**Dado** que a despesa possui campo obrigatório ausente, valor menor ou
igual a zero ou categoria incompatível,\
**quando** o usuário tentar salvar,\
**então** o sistema deverá rejeitar o registro e informar o problema.

### AC-022 --- Classificar despesa fixa ou variável \[P0\]

**Dado** que o usuário está cadastrando uma despesa,\
**quando** selecionar a classificação fixa ou variável,\
**então** a movimentação deverá ser apresentada no grupo correspondente
da visão geral mensal e anual.

### AC-023 --- Editar ou excluir despesa \[P0\]

**Dado** que existe uma despesa cadastrada,\
**quando** o usuário alterar ou excluir o registro,\
**então** o histórico e todos os resumos afetados deverão ser
atualizados sem deixar valores residuais.

### AC-024 --- Registrar investimento \[P1\]

**Dado** que o usuário informa descrição, valor, data e categoria ou
objetivo válido para investimento,\
**quando** salvar,\
**então** o lançamento deverá aparecer na seção de investimentos,
separado das despesas de consumo.

### AC-025 --- Investimento no restante do mês \[P0\]

**Dado** que existem receitas, despesas e investimentos no período,\
**quando** o sistema calcular o restante,\
**então** deverá considerar os investimentos como saída conforme a
fórmula definida no produto:

`Restante = Total de receitas - (Despesas fixas + Despesas variáveis + Investimentos)`

## 8. Histórico financeiro

### AC-026 --- Consultar histórico \[P0\]

**Dado** que o usuário possui movimentações cadastradas,\
**quando** acessar a tela de movimentações,\
**então** deverá visualizar seus registros com data, descrição,
categoria, tipo, forma de pagamento quando aplicável e valor.

### AC-027 --- Ordenação padrão \[P1\]

**Dado** que existem movimentações em datas diferentes,\
**quando** o histórico for aberto sem ordenação personalizada,\
**então** os registros mais recentes deverão aparecer primeiro.

### AC-028 --- Filtrar por período \[P0\]

**Dado** que existem movimentações em diferentes datas,\
**quando** o usuário selecionar um período,\
**então** deverão ser exibidos somente registros dentro do intervalo
informado.

### AC-029 --- Combinar filtros \[P1\]

**Dado** que o usuário seleciona período, tipo, categoria e forma de
pagamento,\
**quando** aplicar os filtros,\
**então** o resultado deverá atender simultaneamente aos critérios
selecionados.

### AC-030 --- Nenhum resultado \[P1\]

**Dado** que os filtros selecionados não correspondem a nenhuma
movimentação,\
**quando** forem aplicados,\
**então** o sistema deverá apresentar um estado vazio informativo, sem
exibir dados não relacionados.

## 9. Visão geral mensal

### AC-031 --- Abrir visão mensal \[P0\]

**Dado** que o usuário está autenticado,\
**quando** acessar a visão geral mensal,\
**então** o sistema deverá apresentar o mês atual por padrão, com os
indicadores e grupos financeiros correspondentes.

### AC-032 --- Indicadores do mês \[P0\]

**Dado** que existem receitas, despesas fixas, despesas variáveis e
investimentos no mês selecionado,\
**quando** o dashboard mensal for carregado,\
**então** deverá apresentar:

-   Total de receitas.
-   Total de despesas fixas.
-   Total de despesas variáveis.
-   Total de investimentos.
-   Total de saídas.
-   Restante do mês.

### AC-033 --- Cálculo do total de saídas \[P0\]

**Dado** que o mês possui despesas fixas, despesas variáveis e
investimentos,\
**quando** o resumo for calculado,\
**então** o total de saídas deverá corresponder à soma desses três
grupos, conforme a política de contabilização aprovada.

### AC-034 --- Cálculo do restante \[P0\]

**Dado** que o total de receitas e o total de saídas estão disponíveis,\
**quando** o resumo for calculado,\
**então** o restante deverá ser igual ao total de receitas menos o total
de saídas.

### AC-035 --- Navegar entre meses \[P0\]

**Dado** que o usuário está na visão mensal,\
**quando** selecionar mês anterior ou próximo mês,\
**então** os indicadores e movimentações deverão corresponder ao novo
mês selecionado.

### AC-036 --- Retornar ao mês atual \[P1\]

**Dado** que o usuário está consultando um mês diferente do atual,\
**quando** acionar a opção de retornar ao mês atual,\
**então** o dashboard deverá apresentar o mês corrente.

### AC-037 --- Mês sem movimentações \[P0\]

**Dado** que não existem movimentações no mês selecionado,\
**quando** o dashboard for carregado,\
**então** os indicadores deverão apresentar valores zerados e as seções
deverão exibir estados vazios apropriados.

### AC-038 --- Acessar lançamento relacionado \[P1\]

**Dado** que uma linha de receita, despesa ou investimento aparece na
visão mensal,\
**quando** o usuário selecionar essa linha,\
**então** deverá conseguir consultar seus detalhes e, conforme suas
permissões, editar ou excluir o lançamento.

## 10. Visão geral anual

### AC-039 --- Abrir visão anual \[P1\]

**Dado** que o usuário acessa a visão geral e seleciona a opção anual,\
**quando** a tela for carregada,\
**então** o sistema deverá apresentar os 12 meses do ano selecionado
organizados em colunas.

### AC-040 --- Exibir grupos financeiros no ano \[P1\]

**Dado** que existem movimentações distribuídas ao longo do ano,\
**quando** a visão anual for carregada,\
**então** deverá apresentar os grupos de receitas, despesas fixas,
despesas variáveis, investimentos e resumo, com os valores de cada mês.

### AC-041 --- Incluir meses sem movimentação \[P1\]

**Dado** que um ou mais meses do ano não possuem lançamentos,\
**quando** a visão anual for exibida,\
**então** esses meses deverão continuar presentes e seus totais deverão
ser apresentados como zero.

### AC-042 --- Total anual \[P1\]

**Dado** que existem valores mensais no ano selecionado,\
**quando** o resumo anual for calculado,\
**então** os totais anuais deverão corresponder à soma dos valores
mensais de cada grupo, respeitando a mesma política de contabilização da
visão mensal.

### AC-043 --- Navegar entre anos \[P1\]

**Dado** que o usuário está na visão anual,\
**quando** selecionar o ano anterior ou próximo ano,\
**então** a tabela deverá apresentar os dados do ano selecionado.

### AC-044 --- Abrir visão mensal a partir do ano \[P1\]

**Dado** que o usuário está na visão anual,\
**quando** selecionar um mês,\
**então** o sistema deverá abrir a visão mensal correspondente ao mês e
ano selecionados.

### AC-045 --- Alternar visualizações \[P1\]

**Dado** que o usuário está na visão geral,\
**quando** alternar entre Mensal e Anual,\
**então** deverá permanecer na seção Visão geral e o contexto de ano
deverá ser preservado sempre que possível.

### AC-046 --- Responsividade da visão anual \[P1\]

**Dado** que o usuário acessa a visão anual em tablet ou smartphone,\
**quando** a tabela ultrapassar a largura disponível,\
**então** a interface deverá permitir consultar os 12 meses sem cortar
valores de forma ilegível, por meio de rolagem horizontal controlada ou
apresentação compacta.

## 11. Cartões de crédito

### AC-047 --- Cadastrar múltiplos cartões \[P0\]

**Dado** que o usuário está autenticado e informa dados válidos de um
cartão,\
**quando** salvar o cadastro,\
**então** o cartão deverá ser criado e aparecer na lista de cartões.

### AC-048 --- Validar dados do cartão \[P0\]

**Dado** que o cartão possui nome ausente, limite negativo ou dia de
fechamento/vencimento inválido,\
**quando** o usuário tentar salvar,\
**então** o sistema deverá rejeitar o cadastro e indicar os campos
inválidos.

### AC-049 --- Gerenciar cartões independentes \[P0\]

**Dado** que o usuário possui dois ou mais cartões,\
**quando** consultar, editar ou visualizar um deles,\
**então** as operações deverão afetar somente o cartão selecionado e
seus próprios registros.

### AC-050 --- Inativar cartão \[P0\]

**Dado** que o usuário possui um cartão com histórico,\
**quando** inativá-lo,\
**então** o histórico e as faturas deverão permanecer consultáveis e
novas compras deverão ser impedidas.

### AC-051 --- Não armazenar dados sensíveis do cartão \[P0\]

**Dado** que o usuário cadastra um cartão,\
**quando** preencher o formulário,\
**então** o sistema não deverá solicitar nem armazenar número completo,
CVV, senha ou credenciais bancárias.

### AC-052 --- Consultar detalhes do cartão \[P1\]

**Dado** que o usuário seleciona um cartão cadastrado,\
**quando** abrir seus detalhes,\
**então** deverá visualizar identificação, limite total, limite
disponível quando calculável, fatura atual, próxima fatura quando houver
dados, compras, histórico de faturas e acesso aos orçamentos daquele
cartão.

## 12. Compras e faturas

### AC-053 --- Registrar compra válida \[P0\]

**Dado** que o usuário seleciona um cartão ativo de sua propriedade e
informa descrição, categoria, data e valor maior que zero,\
**quando** salvar a compra,\
**então** ela deverá ser associada ao cartão, ao usuário e à fatura
correspondente conforme as regras de fechamento aprovadas.

### AC-054 --- Impedir compra em cartão inativo \[P0\]

**Dado** que um cartão está inativo,\
**quando** o usuário tentar registrar uma nova compra nele,\
**então** o sistema deverá impedir a operação.

### AC-055 --- Associar compra à fatura \[P0\]

**Dado** que existe uma compra válida e as regras de fechamento do
cartão estão configuradas,\
**quando** o sistema processar a compra,\
**então** ela deverá ser atribuída ao ciclo de fatura correto conforme a
política aprovada.

### AC-056 --- Calcular total da fatura \[P0\]

**Dado** que uma fatura possui compras ou parcelas atribuídas,\
**quando** seu total for consultado,\
**então** o valor deverá corresponder à soma dos itens pertencentes
àquela fatura.

### AC-057 --- Atualizar fatura após alteração de compra \[P0\]

**Dado** que uma compra associada a uma fatura é editada ou excluída,\
**quando** a operação for concluída,\
**então** o total da fatura e os indicadores relacionados deverão ser
recalculados.

### AC-058 --- Consultar faturas \[P1\]

**Dado** que o cartão possui compras em diferentes ciclos,\
**quando** o usuário consultar suas faturas,\
**então** deverá visualizar os ciclos correspondentes, com datas e
totais disponíveis.

### AC-059 --- Prevenir dupla contagem \[P0\]

**Dado** que uma compra no cartão está incluída em uma fatura,\
**quando** o sistema calcular as despesas da visão geral,\
**então** a compra e o total consolidado da fatura não deverão ser
somados como duas despesas independentes.

### AC-060 --- Pagamento da fatura não é nova despesa de consumo \[P0\]

**Dado** que uma fatura contém compras já registradas como despesas,\
**quando** seu pagamento for registrado conforme a funcionalidade
aprovada,\
**então** o pagamento deverá liquidar a obrigação e não duplicar o valor
como nova despesa de consumo.

### AC-061 --- Parcelamento \[Condicional\]

**Dado** que o parcelamento tenha sido confirmado para o MVP,\
**quando** o usuário registrar uma compra parcelada,\
**então** o sistema deverá distribuir o valor pelas faturas aplicáveis e
garantir que a soma das parcelas corresponda exatamente ao valor
original.

**Dado** que o parcelamento não tenha sido aprovado para o MVP,\
**quando** o usuário registrar uma compra,\
**então** a interface deverá aceitar somente a modalidade definida para
a primeira versão, sem apresentar parcelamento como funcionalidade
disponível.

### AC-062 --- Limite comprometido e disponível \[P1\]

**Dado** que o cartão possui limite total e compras consideradas no
cálculo de comprometimento,\
**quando** os indicadores forem apresentados,\
**então** o limite disponível deverá corresponder ao limite total menos
o valor comprometido, de acordo com a política aprovada.

### AC-101 --- Competência da compra no cartão \[P0\]

**Dado** que uma compra no cartão foi atribuída a um ciclo de fatura,\
**quando** o sistema calcular os indicadores do período,\
**então** a compra deverá ser considerada no período do ciclo da fatura
(mês do vencimento da fatura), conforme `spec.md` §7.2.

### AC-102 --- Compra após o fechamento entra no ciclo seguinte \[P0\]

**Dado** que uma compra foi realizada após a data de fechamento da
fatura,\
**quando** o sistema atribuir a compra a um ciclo,\
**então** a compra deverá pertencer ao ciclo seguinte e ser contabilizada
naquele período, mesmo tendo sido realizada no mês anterior.

### AC-103 --- Compra no dia do fechamento entra no ciclo seguinte \[P0\]

**Dado** que uma compra foi realizada exatamente no dia de fechamento da
fatura,\
**quando** o sistema atribuir a compra a um ciclo,\
**então** a compra deverá pertencer ao ciclo seguinte.

### AC-104 --- Fechamento ou vencimento em mês curto \[P0\]

**Dado** que um cartão possui dia de fechamento ou de vencimento que não
existe em um determinado mês,\
**quando** o sistema calcular as datas da fatura desse mês,\
**então** deverá ser utilizado o último dia do mês correspondente.

### AC-105 --- Primeira fatura após o cadastro do cartão \[P0\]

**Dado** que um cartão acabou de ser cadastrado,\
**quando** o sistema calcular a primeira fatura,\
**então** o primeiro ciclo deverá começar na data de cadastro do cartão
e terminar no dia anterior ao primeiro fechamento posterior ao cadastro.

### AC-106 --- Pagamento da fatura libera limite \[P0\]

**Dado** que uma fatura tem valor em aberto no limite comprometido do
cartão,\
**quando** o pagamento da fatura for registrado (total ou parcial),\
**então** o valor pago deverá ser liberado do limite comprometido, sem
gerar nova despesa de consumo.

### AC-107 --- Editar categoria padrão \[P1\]

**Dado** que existem categorias padrão do sistema,\
**quando** o usuário editar, desativar ou reativar uma categoria,\
**então** a operação deverá ser permitida para categorias padrão e
próprias, preservando o histórico dos lançamentos associados.

## 13. Orçamentos por cartão e categoria

### AC-063 --- Selecionar mês e cartão \[P0\]

**Dado** que o usuário possui cartões cadastrados,\
**quando** acessar Orçamentos,\
**então** deverá conseguir selecionar o mês e o cartão que deseja
acompanhar.

### AC-064 --- Criar orçamento \[P0\]

**Dado** que o usuário selecionou cartão e mês e escolheu uma categoria
válida,\
**quando** informar o valor planejado e salvar,\
**então** o orçamento deverá ser criado para a combinação de usuário,
cartão, mês e categoria.

### AC-065 --- Impedir orçamento duplicado \[P0\]

**Dado** que já existe orçamento para a mesma combinação de usuário,
cartão, mês e categoria,\
**quando** o usuário tentar criar outro,\
**então** o sistema deverá impedir a duplicidade ou direcionar o usuário
para editar o orçamento existente.

### AC-066 --- Orçamentos independentes por cartão \[P0\]

**Dado** que o usuário possui dois cartões e define orçamento para a
mesma categoria em ambos,\
**quando** consultar os orçamentos de cada cartão,\
**então** os valores planejados e gastos deverão ser independentes.

### AC-067 --- Calcular gastos por categoria \[P0\]

**Dado** que existem compras atribuídas ao cartão, mês e categoria
selecionados,\
**quando** o orçamento for consultado,\
**então** o total de gastos deverá corresponder à soma das compras
atribuídas àquela combinação conforme a política aprovada.

### AC-068 --- Calcular restante \[P0\]

**Dado** que existe orçamento definido e gastos registrados para uma
categoria,\
**quando** o sistema calcular o restante,\
**então** deverá aplicar:

`Restante = Orçamento - Gastos`

### AC-069 --- Orçamento não utilizado \[P0\]

**Dado** que existe orçamento e nenhuma compra foi registrada para a
categoria,\
**quando** o usuário consultar a categoria,\
**então** os gastos deverão ser apresentados como R\$ 0,00 e o restante
deverá ser igual ao orçamento.

### AC-070 --- Orçamento totalmente utilizado \[P0\]

**Dado** que os gastos são iguais ao valor orçado,\
**quando** o usuário consultar a categoria,\
**então** o restante deverá ser R\$ 0,00 e a interface deverá indicar
que o orçamento foi totalmente utilizado.

### AC-071 --- Orçamento ultrapassado \[P0\]

**Dado** que os gastos superam o orçamento,\
**quando** o usuário consultar a categoria,\
**então** o restante deverá ser negativo e a interface deverá indicar
que o orçamento foi ultrapassado.

### AC-072 --- Categoria sem orçamento \[P0\]

**Dado** que uma categoria não possui orçamento cadastrado para o cartão
e mês selecionados,\
**quando** for exibida,\
**então** o sistema deverá mostrar "Não definido", sem assumir que o
orçamento é zero e sem calcular percentual de utilização.

### AC-073 --- Editar e remover orçamento \[P0\]

**Dado** que existe um orçamento cadastrado,\
**quando** o usuário alterar ou remover o orçamento,\
**então** a tabela e os totais deverão refletir a alteração, sem excluir
as compras já registradas.

### AC-074 --- Atualizar orçamento após compra \[P0\]

**Dado** que existe orçamento para uma categoria e cartão,\
**quando** uma compra correspondente for criada, editada ou excluída,\
**então** os valores de gastos, restante e percentual deverão ser
atualizados.

### AC-075 --- Totalizador de orçamento \[P1\]

**Dado** que o cartão possui várias categorias orçadas,\
**quando** o totalizador for apresentado,\
**então** deverá somar os valores orçados, gastos e restantes das
categorias exibidas, respeitando categorias sem orçamento definido.

### AC-076 --- Indicador de proximidade do limite \[P1\]

**Dado** que existe um orçamento maior que zero,\
**quando** o percentual de utilização atingir o limite de alerta
definido pelo produto,\
**então** a interface deverá indicar o estado correspondente.

**Bloqueio:** o percentual que caracteriza "próximo do limite" permanece
pendente de confirmação. Não considerar 80% como regra definitiva sem
aprovação.

## 14. Interface, usabilidade e responsividade

### AC-077 --- Navegação principal \[P0\]

**Dado** que o usuário está autenticado,\
**quando** visualizar a navegação principal,\
**então** deverá encontrar acesso às seções Visão geral, Movimentações,
Cartões, Orçamentos, Categorias e Configurações, conforme o escopo
implementado.

### AC-078 --- Identidade visual \[P1\]

**Dado** que o usuário navega pelas telas principais,\
**quando** visualizar os componentes,\
**então** deverá encontrar padrões consistentes de cores, tipografia,
botões, campos, tabelas e indicadores, alinhados ao protótipo de
referência.

### AC-079 --- Simplicidade de cadastro \[P0\]

**Dado** que o usuário deseja registrar uma receita ou despesa,\
**quando** abrir o formulário,\
**então** deverá encontrar somente os campos necessários ao tipo de
movimentação selecionado, sem opções irrelevantes.

### AC-080 --- Estados de carregamento e erro \[P0\]

**Dado** que uma operação está sendo processada ou falha,\
**quando** a interface aguardar ou receber uma resposta,\
**então** deverá apresentar estado de carregamento, mensagem de sucesso
ou mensagem de erro apropriada, sem deixar o usuário sem retorno.

### AC-081 --- Confirmação de exclusão \[P1\]

**Dado** que o usuário solicita excluir uma movimentação, compra ou
orçamento,\
**quando** a ação puder causar perda de informação,\
**então** o sistema deverá solicitar confirmação antes de concluir a
operação.

### AC-082 --- Uso em computador \[P0\]

**Dado** que o usuário acessa o sistema em computador,\
**quando** navegar pelas funcionalidades principais,\
**então** deverá conseguir utilizar menu, formulários, tabelas e ações
sem sobreposição ou corte de conteúdo.

### AC-083 --- Uso em smartphone \[P0\]

**Dado** que o usuário acessa o sistema em smartphone,\
**quando** utilizar as funcionalidades principais,\
**então** a navegação, os formulários, os indicadores e as listas
deverão adaptar-se à tela e permanecer utilizáveis.

### AC-084 --- Uso em tablet \[P1\]

**Dado** que o usuário acessa o sistema em tablet,\
**quando** utilizar as funcionalidades principais,\
**então** os componentes deverão adaptar-se ao espaço disponível, sem
perda de funcionalidade.

### AC-085 --- Acessibilidade básica \[P1\]

**Dado** que o usuário navega por teclado ou utiliza tecnologias
assistivas,\
**quando** acessar os controles e formulários principais,\
**então** os elementos deverão possuir rótulos, foco visível, ordem de
navegação coerente e mensagens compreensíveis.

### AC-086 --- Significado não depende apenas da cor \[P1\]

**Dado** que a interface utiliza cores para representar receitas,
despesas e estados de orçamento,\
**quando** apresentar essas informações,\
**então** deverá também utilizar textos, ícones ou rótulos que
comuniquem o significado.

## 15. Segurança, integridade e qualidade técnica

### AC-087 --- Validação no servidor \[P0\]

**Dado** que uma requisição envia dados inválidos diretamente à API, sem
passar pela interface,\
**quando** o servidor processar a requisição,\
**então** deverá validar os dados e rejeitar a operação inválida.

### AC-088 --- Precisão monetária \[P0\]

**Dado** que o sistema armazena e calcula valores financeiros,\
**quando** realizar operações de soma, subtração ou distribuição de
parcelas,\
**então** deverá utilizar representação decimal apropriada e evitar
erros decorrentes de ponto flutuante.

### AC-089 --- Formatação brasileira \[P0\]

**Dado** que um valor monetário é apresentado ao usuário,\
**quando** for exibido na interface,\
**então** deverá utilizar o padrão brasileiro de reais, como
`R$ 1.234,56`.

### AC-090 --- Consistência após alteração \[P0\]

**Dado** que uma movimentação, compra ou orçamento é alterado ou
excluído,\
**quando** a operação for concluída,\
**então** todos os indicadores, totais, faturas e orçamentos
relacionados deverão refletir os dados atuais.

### AC-091 --- Compatibilidade com navegadores modernos \[P1\]

**Dado** que o usuário utiliza um navegador moderno suportado pelo
projeto,\
**quando** acessar as telas principais,\
**então** os recursos essenciais deverão funcionar sem erros que impeçam
a utilização.

### AC-092 --- Segredos fora do código \[P0\]

**Dado** que a aplicação utiliza credenciais de banco, tokens ou outras
chaves,\
**quando** o projeto for executado ou publicado,\
**então** esses segredos deverão ser obtidos de configuração segura e
não deverão estar expostos no repositório.

### AC-093 --- HTTPS em produção \[P0\]

**Dado** que a aplicação está publicada,\
**quando** o usuário acessar o sistema,\
**então** a comunicação deverá ocorrer por HTTPS.

### AC-094 --- Logs sem exposição desnecessária \[P1\]

**Dado** que a aplicação registra eventos e erros,\
**quando** gerar logs,\
**então** não deverá registrar senhas, tokens ou detalhes financeiros
desnecessários.

### AC-095 --- Backup e restauração \[P1\]

**Dado** que o banco de dados contém informações de usuários,\
**quando** a rotina de backup for executada,\
**então** deverá gerar uma cópia recuperável conforme o procedimento
documentado. A restauração deverá ser testada antes da publicação
considerada estável.

## 16. Cenários de reconciliação com a planilha

A planilha utilizada pelo responsável pelo produto é a principal
referência funcional. Antes de considerar os cálculos financeiros
aceitos, deverão ser selecionados meses reais ou conjuntos de dados
representativos e comparados com os resultados do sistema.

### AC-096 --- Comparar totais mensais \[P0\]

**Dado** que um mês da planilha foi reproduzido no sistema com as mesmas
receitas, despesas fixas, despesas variáveis e investimentos,\
**quando** os totais forem calculados,\
**então** os valores de cada grupo, total de saídas e restante deverão
coincidir com a planilha, respeitando as regras de contabilização
aprovadas.

### AC-097 --- Comparar visão anual \[P1\]

**Dado** que os dados dos 12 meses de um ano foram reproduzidos no
sistema,\
**quando** a visão anual for consultada,\
**então** os valores por mês e os totais anuais deverão corresponder à
soma dos dados utilizados na visão mensal.

### AC-098 --- Comparar gastos do cartão \[P0\]

**Dado** que compras de um cartão foram reproduzidas com as mesmas
datas, categorias e valores da planilha,\
**quando** o usuário consultar os gastos e a fatura,\
**então** os totais deverão corresponder aos lançamentos atribuídos ao
mesmo ciclo, segundo as regras aprovadas.

### AC-099 --- Comparar orçamento por categoria \[P0\]

**Dado** que foram cadastrados os mesmos valores orçados e as mesmas
compras de uma categoria para determinado cartão e mês,\
**quando** o sistema calcular planejado, gasto e restante,\
**então** os três valores deverão corresponder à planilha.

### AC-100 --- Reconciliar divergências \[P0\]

**Dado** que o resultado do sistema difere da planilha,\
**quando** a divergência for identificada,\
**então** a equipe deverá registrar a causa --- regra de período,
classificação, fatura, duplicidade, arredondamento ou dado de entrada
--- e obter validação do responsável pelo produto antes de considerar o
cenário aprovado.

## 17. Decisões pendentes que bloqueiam critérios específicos

Os critérios abaixo não devem ser considerados definitivamente aprovados
até que as decisões correspondentes sejam registradas em `spec.md`:

  -----------------------------------------------------------------------
  Tema pendente           Critérios afetados      Decisão necessária
  ----------------------- ----------------------- -----------------------
  Política de             AC-032 a AC-034, AC-055 Definir quando a compra
  contabilização de       a AC-060, AC-096 a      e a fatura impactam o
  compras e faturas       AC-100                  restante e como evitar
                                                  dupla contagem.

  Mês de referência do    AC-063, AC-067, AC-074, Definir se o orçamento
  orçamento               AC-098 e AC-099         considera data da
                                                  compra ou mês da
                                                  fatura.

  Compra no dia do        AC-055 e AC-098         Definir a qual fatura a
  fechamento                                      compra será atribuída.

  Parcelamento no MVP     AC-061 e AC-062         Confirmar se
                                                  parcelamento será
                                                  implementado na
                                                  primeira versão.

  Cálculo do limite       AC-062                  Definir o tratamento de
  comprometido                                    parcelas futuras e
                                                  pagamentos.

  Pagamento parcial ou    AC-060                  Confirmar se o registro
  total da fatura                                 de pagamento fará parte
                                                  do MVP e como será
                                                  representado.

  Percentual de alerta do AC-076                  Aprovar o percentual
  orçamento                                       que caracteriza
                                                  "próximo do limite".

  Recorrência de despesas AC-022 e AC-096         Definir se os
  fixas                                           lançamentos serão
                                                  manuais mês a mês ou
                                                  gerados
                                                  automaticamente.
  -----------------------------------------------------------------------

Enquanto uma decisão estiver pendente, a funcionalidade correspondente
poderá ser testada em nível de interface ou com comportamento provisório
explicitamente identificado, mas não deverá ser declarada plenamente
aceita.

## 18. Critérios gerais de aceite do MVP

O MVP do meuSaldo poderá ser considerado aceito quando todos os itens P0
aplicáveis forem aprovados e as pendências impeditivas tiverem sido
resolvidas.

-   [ ] Um usuário consegue criar uma conta, entrar e sair do sistema.
-   [ ] Os dados financeiros de usuários diferentes permanecem isolados.
-   [ ] O usuário consegue criar, editar, consultar e excluir receitas e
    despesas.
-   [ ] O usuário consegue organizar movimentações por categorias.
-   [ ] O usuário consegue registrar investimentos e consultá-los
    separadamente.
-   [ ] O histórico permite consultar e filtrar movimentações.
-   [ ] A visão mensal apresenta os totais e o restante corretamente.
-   [ ] A visão anual apresenta os 12 meses e mantém consistência com a
    visão mensal.
-   [ ] O usuário consegue cadastrar e gerenciar múltiplos cartões.
-   [ ] O usuário consegue registrar compras e consultar as faturas
    correspondentes.
-   [ ] O sistema não duplica despesas entre compras e pagamentos de
    fatura.
-   [ ] O usuário consegue criar orçamentos por cartão, categoria e mês.
-   [ ] O sistema calcula corretamente planejado, gasto e restante.
-   [ ] Os cálculos utilizam precisão monetária adequada.
-   [ ] As funcionalidades principais são utilizáveis em computador e
    smartphone.
-   [ ] Os testes automatizados essenciais passam.
-   [ ] A aplicação publicada utiliza HTTPS e configuração segura.
-   [ ] Os resultados financeiros foram comparados com dados
    representativos da planilha e validados pelo responsável pelo
    produto.

## 19. Registro de validação

Preencher ao final de cada ciclo de validação.

  Informação                   Registro
  ---------------------------- -----------------------------------------------
  Versão avaliada              A preencher
  Data da validação            A preencher
  Responsável pela validação   A preencher
  Ambiente                     Desenvolvimento / Homologação / Produção
  Cenários executados          A preencher
  Cenários aprovados           A preencher
  Cenários reprovados          A preencher
  Pendências conhecidas        A preencher
  Resultado                    Aprovado / Aprovado com ressalvas / Reprovado

### Resultado final

-   [ ] **Aprovado:** critérios obrigatórios atendidos e sem pendências
    impeditivas.
-   [ ] **Aprovado com ressalvas:** critérios obrigatórios atendidos,
    com pendências não impeditivas registradas.
-   [ ] **Reprovado:** existem critérios obrigatórios não atendidos ou
    falhas que comprometem segurança, integridade ou cálculos.

------------------------------------------------------------------------

**Princípio de validação:** o meuSaldo deve ser simples de utilizar, mas
seus resultados financeiros precisam ser confiáveis. A interface só será
considerada pronta quando facilitar o uso sem comprometer a precisão, a
privacidade e a consistência dos dados.
