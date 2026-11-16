# spec.md --- meuSaldo

**Projeto:** meuSaldo --- Controle Financeiro Pessoal\
**Versão:** 0.1 --- Especificação inicial do MVP\
**Documento relacionado:** `requirements.md`

------------------------------------------------------------------------

## 1. Objetivo deste documento

Este documento detalha o comportamento esperado das funcionalidades do
meuSaldo, descrevendo fluxos, regras de negócio, validações e critérios
de aceitação para orientar o desenvolvimento.

O foco é transformar os requisitos iniciais em comportamentos
verificáveis, mantendo como princípio central a simplicidade de uso.

Decisões ainda não confirmadas estão identificadas como **Pendente de
definição** e não devem ser consideradas regras definitivas.

## 2. Visão do produto

O meuSaldo é uma aplicação web para controle financeiro pessoal. Cada
usuário poderá registrar manualmente suas receitas, despesas e compras
no cartão de crédito, além de consultar um resumo da própria situação
financeira.

A aplicação deverá priorizar:

-   Rapidez no registro de movimentações.
-   Clareza na apresentação dos valores.
-   Navegação simples e intuitiva.
-   Separação segura dos dados de cada usuário.
-   Boa experiência em computadores e dispositivos móveis.

## 3. Perfis e permissões

### 3.1. Usuário comum

O usuário autenticado poderá:

-   Consultar seu dashboard.
-   Criar, visualizar, editar e excluir suas receitas.
-   Criar, visualizar, editar e excluir suas despesas.
-   Consultar e filtrar seu histórico financeiro.
-   Criar e gerenciar categorias.
-   Cadastrar e gerenciar seus cartões de crédito.
-   Registrar compras e consultar faturas dos próprios cartões.
-   Atualizar os dados permitidos de sua conta.

O usuário não poderá visualizar ou modificar dados pertencentes a outra
conta.

### 3.2. Administrador

O administrador poderá gerenciar contas e configurações administrativas
necessárias à operação do sistema.

O perfil administrativo não deverá conceder acesso automático aos
valores, descrições ou movimentações financeiras particulares dos
usuários. Qualquer necessidade excepcional de acesso deverá ser definida
por política específica, justificada e auditável.

## 4. Conceitos e definições

  -----------------------------------------------------------------------
  Termo                               Definição
  ----------------------------------- -----------------------------------
  Receita                             Entrada de dinheiro registrada pelo
                                      usuário.

  Despesa                             Saída de dinheiro registrada pelo
                                      usuário.

  Movimentação                        Registro financeiro do tipo receita
                                      ou despesa.

  Categoria                           Classificação utilizada para
                                      organizar movimentações.

  Saldo do período                    Resultado das receitas menos as
                                      despesas consideradas no período.

  Cartão                              Instrumento de crédito cadastrado
                                      pelo usuário para acompanhar
                                      compras.

  Compra no cartão                    Despesa realizada com um cartão de
                                      crédito.

  Fatura                              Conjunto de compras atribuídas a um
                                      ciclo de cobrança do cartão.

  Fechamento                          Data a partir da qual novas compras
                                      passam, em regra, para a próxima
                                      fatura.

  Vencimento                          Data limite de pagamento da fatura.
  -----------------------------------------------------------------------

## 5. Regras gerais de dados

1.  Todos os registros financeiros deverão pertencer a um usuário.
2.  Valores monetários deverão ser armazenados com precisão decimal,
    evitando tipos de ponto flutuante inadequados para cálculos
    financeiros.
3.  A moeda inicial será o real brasileiro (BRL), com apresentação no
    padrão `R$ 1.234,56`.
4.  Datas deverão ser armazenadas e exibidas de maneira consistente,
    respeitando o fuso horário definido para a aplicação.
5.  Registros financeiros deverão possuir identificador único, usuário
    proprietário e datas de criação e atualização.
6.  A API deverá validar os dados recebidos, mesmo quando a interface
    também realizar validações.
7.  Consultas, alterações e exclusões deverão sempre verificar a
    propriedade do registro pelo usuário autenticado.
8.  Exclusões de movimentações deverão atualizar os totais e indicadores
    apresentados no dashboard.
9.  O sistema deverá impedir valores inválidos, como valores negativos
    em lançamentos comuns, salvo se uma regra específica futura permitir
    ajustes ou estornos.
10. O sistema deverá manter consistência entre compras, faturas e
    pagamentos, evitando contabilizar a mesma despesa duas vezes.

## 6. Especificação das funcionalidades

### 6.1. Cadastro de usuário

**Descrição:** permitir que uma pessoa crie uma conta para utilizar o
sistema.

**Dados mínimos previstos:**

-   Nome.
-   E-mail.
-   Senha.
-   Confirmação de senha, na interface.

**Regras de negócio:**

-   O e-mail deverá ser obrigatório e possuir formato válido.
-   O e-mail deverá ser único no sistema.
-   A senha deverá atender a uma política mínima de segurança, a ser
    definida na implementação.
-   A senha nunca deverá ser armazenada em texto puro.
-   A aplicação deverá apresentar mensagens claras em caso de dados
    inválidos ou e-mail já cadastrado.

**Fluxo principal:**

1.  A pessoa acessa a tela de cadastro.
2.  Informa nome, e-mail e senha.
3.  O sistema valida os campos.
4.  O sistema cria a conta.
5.  A pessoa recebe confirmação do cadastro e poderá acessar o sistema
    conforme a política de autenticação definida.

**Critérios de aceitação:**

-   Dado um e-mail ainda não cadastrado e dados válidos, quando o
    formulário for enviado, então a conta deverá ser criada.
-   Dado um e-mail já utilizado, quando houver tentativa de cadastro,
    então o sistema deverá rejeitar a operação e informar o motivo sem
    expor dados de terceiros.
-   Dada uma senha inválida segundo a política definida, o cadastro
    deverá ser recusado.

### 6.2. Login e logout

**Descrição:** permitir que usuários acessem e encerrem suas sessões.

**Regras de negócio:**

-   O login deverá validar as credenciais.
-   Credenciais incorretas deverão gerar mensagem genérica, sem revelar
    se o e-mail existe.
-   Rotas privadas deverão exigir autenticação.
-   O logout deverá invalidar ou encerrar a sessão conforme o mecanismo
    adotado.
-   Tokens e credenciais deverão ser tratados com segurança.

**Critérios de aceitação:**

-   Um usuário com credenciais válidas consegue acessar as áreas
    privadas.
-   Um usuário sem autenticação não consegue consultar dados privados.
-   Após logout, a sessão não poderá continuar autorizando operações
    protegidas.

### 6.3. Categorias

**Descrição:** organizar receitas e despesas por categorias.

**Campos previstos:**

-   Nome.
-   Tipo: receita ou despesa.
-   Cor ou ícone, opcionais.
-   Identificação do usuário ou indicação de categoria padrão do
    sistema.

**Regras de negócio:**

-   Uma categoria deverá ser compatível com o tipo da movimentação.
-   O usuário poderá utilizar categorias padrão disponibilizadas pelo
    sistema.
-   O usuário poderá criar categorias próprias.
-   O nome da categoria será obrigatório.
-   O sistema deverá evitar duplicidade de nomes para o mesmo usuário e
    tipo.
-   Uma categoria já utilizada não deverá ser removida sem tratamento
    dos registros associados. A opção preferencial é desativá-la ou
    solicitar a reclassificação das movimentações.

**Pendente de definição:** decidir se categorias padrão poderão ser
editadas e quais categorias iniciais serão disponibilizadas.

**Critérios de aceitação:**

-   O usuário consegue criar uma categoria válida.
-   Uma despesa não pode ser classificada em uma categoria exclusiva de
    receita.
-   Uma categoria utilizada não pode causar perda ou inconsistência dos
    lançamentos ao ser desativada.

### 6.4. Cadastro de receitas

**Descrição:** registrar entradas financeiras do usuário.

**Campos previstos:**

-   Descrição.
-   Valor.
-   Data de recebimento.
-   Categoria.
-   Observações, opcionais.

**Regras de negócio:**

-   Descrição, valor, data e categoria serão obrigatórios.
-   O valor deverá ser maior que zero.
-   A categoria deverá ser do tipo receita.
-   A receita será considerada no período correspondente à data de
    recebimento.
-   O registro deverá ser associado ao usuário autenticado.
-   O usuário poderá editar ou excluir somente suas próprias receitas.

**Fluxo principal:**

1.  O usuário seleciona a opção de adicionar receita.
2.  Informa descrição, valor, data e categoria.
3.  O sistema valida os campos.
4.  O sistema salva a receita.
5.  O sistema atualiza os indicadores financeiros afetados.

**Critérios de aceitação:**

-   Uma receita válida é salva e aparece no histórico.
-   O total de receitas do período é atualizado após o cadastro.
-   A edição de uma receita atualiza os totais do período anterior e do
    novo período, quando aplicável.
-   A exclusão de uma receita remove seu efeito dos cálculos.

### 6.5. Cadastro de despesas

**Descrição:** registrar saídas financeiras do usuário.

**Campos previstos:**

-   Descrição.
-   Valor.
-   Data da despesa.
-   Categoria.
-   Forma de pagamento.
-   Observações, opcionais.

**Formas de pagamento inicialmente previstas:**

-   Dinheiro.
-   Pix.
-   Débito.
-   Cartão de crédito.
-   Outra forma, se necessário.

**Regras de negócio:**

-   Descrição, valor, data, categoria e forma de pagamento serão
    obrigatórios.
-   O valor deverá ser maior que zero.
-   A categoria deverá ser do tipo despesa.
-   A despesa deverá ser considerada no período correspondente à data da
    despesa, respeitando a regra de contabilização definida para cada
    forma de pagamento.
-   Quando a forma de pagamento for cartão de crédito, a compra deverá
    estar associada a um cartão cadastrado.
-   O sistema deverá impedir que uma mesma compra seja registrada
    simultaneamente como despesa comum e compra de cartão, gerando
    duplicidade nos totais.
-   O usuário poderá editar ou excluir somente suas próprias despesas.

**Critérios de aceitação:**

-   Uma despesa válida é salva e aparece no histórico.
-   O total de despesas é atualizado conforme as regras de período.
-   A edição ou exclusão atualiza os indicadores relacionados.
-   Uma despesa paga com cartão fica vinculada ao cartão e à fatura
    correspondente.

### 6.6. Histórico financeiro

**Descrição:** apresentar as movimentações cadastradas pelo usuário.

**Informações exibidas:**

-   Data.
-   Descrição.
-   Categoria.
-   Tipo de movimentação.
-   Forma de pagamento, quando aplicável.
-   Valor.

**Filtros previstos:**

-   Período.
-   Tipo: receita ou despesa.
-   Categoria.
-   Forma de pagamento.

**Regras de negócio:**

-   O histórico deverá exibir somente registros do usuário autenticado.
-   A ordenação padrão deverá apresentar as movimentações mais recentes
    primeiro.
-   Os filtros poderão ser combinados.
-   O sistema deverá apresentar um estado vazio quando não houver
    registros para os filtros selecionados.
-   O usuário poderá acessar as opções de edição e exclusão de seus
    próprios registros.

**Critérios de aceitação:**

-   O usuário visualiza somente suas movimentações.
-   Os filtros retornam registros compatíveis com os critérios
    selecionados.
-   A ordenação padrão apresenta primeiro os registros mais recentes.

### 6.7. Dashboard

**Descrição:** apresentar uma visão resumida e objetiva da situação
financeira.

**Indicadores previstos:**

1.  Total de receitas do período.
2.  Total de despesas do período.
3.  Saldo do período.
4.  Total de compras no cartão de crédito no período, apresentado
    separadamente conforme a regra de contabilização.
5.  Últimas movimentações.
6.  Despesas agrupadas por categoria.

**Regras de negócio:**

-   O período padrão será o mês atual.
-   O usuário poderá consultar outro período por meio de um seletor.
-   Todos os indicadores deverão considerar os filtros de período
    aplicáveis.
-   O saldo deverá ser calculado conforme a regra financeira descrita na
    seção 7.
-   O dashboard deverá apresentar valores zerados e mensagens adequadas
    quando não houver movimentações.
-   A interface deverá priorizar leitura rápida, sem excesso de gráficos
    ou elementos visuais.

**Critérios de aceitação:**

-   Os indicadores correspondem aos registros do período selecionado.
-   Ao alterar uma movimentação, os valores do dashboard são
    atualizados.
-   Um usuário não visualiza indicadores calculados com dados de outro
    usuário.

### 6.8. Cadastro de cartões de crédito

**Descrição:** permitir que o usuário cadastre cartões para acompanhar
compras e faturas.

**Campos previstos:**

-   Nome ou identificação do cartão.
-   Limite total.
-   Dia de fechamento da fatura.
-   Dia de vencimento.
-   Situação: ativo ou inativo.

**Regras de negócio:**

-   O nome do cartão será obrigatório.
-   O limite deverá ser maior ou igual a zero.
-   Os dias de fechamento e vencimento deverão respeitar os dias válidos
    do calendário mensal.
-   O sistema não deverá solicitar nem armazenar número completo do
    cartão, código de segurança (CVV), senha ou outros dados de
    autenticação bancária.
-   O usuário poderá editar ou inativar seus próprios cartões.
-   Um cartão inativo não deverá aceitar novas compras, mas seu
    histórico deverá permanecer disponível.

**Critérios de aceitação:**

-   O usuário consegue cadastrar um cartão com dados válidos.
-   O usuário consegue consultar e editar os dados permitidos.
-   Um cartão inativo mantém o histórico e não aceita novos lançamentos.

### 6.9. Compras no cartão de crédito

**Descrição:** registrar compras feitas com um cartão cadastrado.

**Campos previstos:**

-   Descrição da compra.
-   Valor total.
-   Data da compra.
-   Cartão utilizado.
-   Categoria.
-   Quantidade de parcelas, inicialmente igual a 1 quando não parcelada.
-   Observações, opcionais.

**Regras de negócio:**

-   A compra deverá estar associada a um cartão ativo pertencente ao
    usuário.
-   O valor total deverá ser maior que zero.
-   A quantidade de parcelas deverá ser um número inteiro maior ou igual
    a 1.
-   O sistema deverá distribuir o valor entre as parcelas, tratando
    eventuais diferenças de centavos para que a soma das parcelas
    corresponda exatamente ao valor total.
-   Cada parcela deverá ser atribuída a uma fatura conforme as datas de
    compra, fechamento e vencimento.
-   A compra deverá ser contabilizada uma única vez nos indicadores de
    despesas, segundo a política de contabilização escolhida.
-   O usuário poderá consultar, editar ou excluir suas próprias compras,
    respeitando o impacto nas faturas.

**Pendente de definição:** confirmar se o MVP terá suporte a compras
parceladas. Caso não seja essencial, recomenda-se iniciar com compras à
vista no cartão e adicionar parcelamento em uma evolução próxima.

**Critérios de aceitação:**

-   Uma compra válida é associada ao cartão e aparece na fatura correta.
-   O valor comprometido do cartão é atualizado.
-   O total das parcelas corresponde ao valor original da compra.
-   A exclusão de uma compra atualiza a fatura e os indicadores sem
    deixar parcelas órfãs.

### 6.10. Faturas

**Descrição:** agrupar compras de um cartão em ciclos de cobrança.

**Informações previstas:**

-   Cartão.
-   Período da fatura.
-   Data de fechamento.
-   Data de vencimento.
-   Total da fatura.
-   Situação da fatura, conforme evolução da funcionalidade.

**Regras de negócio:**

-   A fatura deverá reunir as compras atribuídas ao respectivo ciclo.
-   A compra deverá ser atribuída a uma fatura de acordo com a data da
    compra e o dia de fechamento.
-   Compras realizadas após o fechamento deverão ser atribuídas ao ciclo
    seguinte.
-   O cálculo deverá tratar corretamente meses com quantidades
    diferentes de dias.
-   O sistema deverá apresentar o total das compras atribuídas à fatura.
-   O tratamento de pagamento parcial, pagamento total e atraso deverá
    ser definido antes de implementar baixa de fatura.

**Pendente de definição:** especificar como será calculada a primeira
fatura após o cadastro do cartão e como serão tratadas compras
realizadas exatamente no dia do fechamento.

### 6.11. Limite do cartão

**Descrição:** apresentar o limite total e o valor comprometido com
compras.

**Regra inicial sugerida:**

`Limite disponível = Limite total - Valor comprometido`

O conceito de valor comprometido deverá considerar compras ainda não
pagas e parcelas futuras, conforme a política de limite aprovada.

**Pendente de definição:** decidir se o limite disponível será calculado
considerando todas as parcelas futuras ou apenas compras lançadas em
faturas ainda não pagas.

## 7. Regras de cálculo financeiro

Esta seção é especialmente importante para evitar divergências nos
indicadores e dupla contagem de despesas.

### 7.1. Saldo do período

A fórmula conceitual é:

`Saldo do período = Receitas consideradas - Despesas consideradas`

O sistema deverá definir uma única política de contabilização para cada
tipo de movimentação. A data utilizada para agrupar os valores deverá
ser consistente com essa política.

### 7.2. Compras no cartão e pagamento da fatura

Uma compra no cartão representa a despesa de consumo. O pagamento da
fatura representa a liquidação de uma obrigação já registrada.

Portanto, o sistema não deverá somar a compra e o pagamento da fatura
como duas despesas independentes no mesmo cálculo de resultado
financeiro.

**Regra recomendada para o MVP:**

-   Registrar a compra no cartão como despesa.
-   Agrupar a compra na fatura correspondente.
-   Tratar o pagamento da fatura como liquidação/baixa da fatura, e não
    como uma nova despesa de consumo.
-   Exibir separadamente o valor das faturas e o total de compras no
    cartão.

Se o sistema vier a oferecer controle de contas bancárias e fluxo de
caixa por conta, a liquidação da fatura poderá gerar uma saída de caixa
vinculada à obrigação, sem duplicar a despesa no resultado.

### 7.3. Precisão monetária

-   Utilizar tipo decimal no banco de dados.
-   Definir escala de duas casas decimais para valores em reais, quando
    apropriado.
-   Garantir que o arredondamento de parcelas não altere a soma do valor
    original.
-   Formatar valores para exibição no padrão brasileiro.

## 8. Requisitos de interface e experiência

### 8.1. Diretrizes visuais

A interface deverá ser minimalista, com hierarquia visual clara e poucos
elementos por tela.

Diretrizes:

-   Menu de navegação enxuto.
-   Dashboard como ponto de entrada após o login.
-   Ação de adicionar movimentação facilmente identificável.
-   Formulários curtos e objetivos.
-   Valores financeiros com destaque visual adequado.
-   Cores consistentes para receitas, despesas e saldo, sem depender
    exclusivamente da cor para transmitir significado.
-   Mensagens claras de sucesso, erro e confirmação.
-   Estados de carregamento e telas vazias bem definidos.

### 8.2. Navegação inicial sugerida

-   Visão geral.
-   Movimentações.
-   Cartões.
-   Categorias.
-   Minha conta.

A administração deverá ficar em uma área separada, disponível somente
para administradores.

### 8.3. Responsividade e acessibilidade

-   Os formulários deverão ser utilizáveis em telas pequenas.
-   Botões e campos deverão possuir rótulos claros.
-   A interface deverá permitir navegação por teclado nas operações
    essenciais.
-   Contraste e tamanho de texto deverão favorecer a leitura.
-   Mensagens de validação deverão identificar o campo que precisa de
    correção.

## 9. Segurança e privacidade

1.  Todas as rotas privadas da API deverão exigir autenticação.
2.  A autorização deverá ser validada no back-end, não apenas na
    interface.
3.  Toda consulta ou alteração de dados financeiros deverá aplicar o
    identificador do usuário autenticado.
4.  Senhas deverão ser armazenadas com algoritmo apropriado de hash.
5.  A comunicação em produção deverá utilizar HTTPS.
6.  Segredos, chaves e credenciais não deverão ser armazenados no
    repositório de código.
7.  Entradas deverão ser validadas e tratadas para reduzir riscos de
    ataques.
8.  O sistema deverá evitar exposição de dados financeiros em logs.
9.  Deverá existir estratégia de backup do banco de dados.
10. O sistema deverá coletar apenas os dados pessoais necessários ao
    funcionamento.

## 10. Requisitos técnicos iniciais

Tecnologias previstas:

-   Front-end: Vue.js 3.
-   Estilização: Tailwind CSS.
-   Back-end: Python com FastAPI.
-   Banco de dados: PostgreSQL.
-   Autenticação: mecanismo baseado em tokens, com estratégia de
    armazenamento e renovação definida no desenho técnico.
-   Versionamento: Git e GitHub.
-   Hospedagem: VPS ou plataforma cloud.

### 10.1. Organização lógica sugerida

A solução deverá separar responsabilidades em:

-   Interface e componentes visuais.
-   Comunicação com a API.
-   Autenticação e autorização.
-   Regras de negócio.
-   Persistência e acesso aos dados.
-   Validação e tratamento de erros.

A estrutura física de pastas e módulos deverá ser definida no documento
`design.md`.

## 11. Critérios de aceitação do MVP

-   [ ] Um usuário consegue criar uma conta.
-   [ ] Um usuário consegue realizar login e logout.
-   [ ] Um usuário consegue cadastrar, editar e excluir receitas.
-   [ ] Um usuário consegue cadastrar, editar e excluir despesas.
-   [ ] As movimentações podem ser classificadas por categoria.
-   [ ] O histórico permite consultar e filtrar movimentações.
-   [ ] O dashboard apresenta receitas, despesas e saldo do período.
-   [ ] Os cálculos são consistentes e não duplicam compras no cartão.
-   [ ] Um usuário consegue cadastrar e gerenciar cartões.
-   [ ] Um usuário consegue registrar compras no cartão e consultar suas
    faturas, conforme o escopo de cartão aprovado.
-   [ ] Os dados de um usuário não podem ser acessados por outro.
-   [ ] As telas essenciais funcionam em computador e smartphone.
-   [ ] A aplicação apresenta mensagens claras para erros e operações
    concluídas.

## 12. Decisões pendentes

As decisões abaixo precisam ser confirmadas antes ou durante a
implementação das funcionalidades correspondentes.

  ------------------------------------------------------------------------
  ID                      Decisão                  Recomendação inicial
  ----------------------- ------------------------ -----------------------
  DP-01                   O sistema terá somente   Somente individual no
                          controle individual ou   MVP.
                          permitirá contas         
                          compartilhadas?          

  DP-02                   Categorias serão fixas,  Disponibilizar
                          personalizáveis ou       categorias padrão e
                          ambas?                   permitir categorias
                                                   próprias.

  DP-03                   O controle de cartão     Começar com compras à
                          terá compras parceladas  vista, se a
                          no MVP?                  simplicidade for
                                                   prioridade.

  DP-04                   Como será definido o     Definir uma política
                          saldo: por data da       única e explicá-la na
                          movimentação ou data     interface.
                          efetiva de               
                          recebimento/pagamento?   

  DP-05                   O sistema permitirá      Sim, como liquidação,
                          registrar pagamento de   sem gerar uma segunda
                          fatura?                  despesa de consumo.

  DP-06                   Como será calculado o    Considerar compras e
                          limite disponível?       parcelas ainda não
                                                   pagas, após definição
                                                   da regra de negócio.

  DP-07                   Como tratar compras      Definir uma regra
                          realizadas no dia do     explícita e testável.
                          fechamento?              

  DP-08                   Haverá recuperação de    Recomendada antes de
                          senha por e-mail no MVP? disponibilizar
                                                   publicamente.

  DP-09                   O sistema terá           Deixar para uma versão
                          exportação de dados?     posterior.
  ------------------------------------------------------------------------

## 13. Estratégia de implementação sugerida

A implementação deverá ocorrer em incrementos pequenos, mantendo o
sistema utilizável ao final de cada etapa.

1.  **Fundação:** configurar projeto, banco de dados, API e front-end.
2.  **Acesso:** implementar cadastro, login, logout e proteção de rotas.
3.  **Categorias:** implementar categorias padrão e personalizadas.
4.  **Movimentações:** implementar receitas, despesas, edição, exclusão
    e histórico.
5.  **Dashboard:** implementar indicadores e filtros de período.
6.  **Cartões:** implementar cadastro de cartões, compras e faturas
    conforme decisões aprovadas.
7.  **Qualidade:** validar segurança, responsividade, cálculos e
    critérios de aceitação.
8.  **Publicação:** preparar ambiente de produção, HTTPS, variáveis de
    ambiente e backups.

## 14. Relação com os demais documentos

  -----------------------------------------------------------------------
  Documento                           Responsabilidade
  ----------------------------------- -----------------------------------
  `requirements.md`                   Define problema, objetivos,
                                      público, escopo e requisitos
                                      gerais.

  `spec.md`                           Detalha funcionalidades, regras de
                                      negócio, fluxos e critérios de
                                      aceitação.

  `design.md`                         Descreverá arquitetura,
                                      componentes, banco de dados, APIs e
                                      decisões técnicas.

  `tasks.md`                          Decomporá o trabalho em tarefas
                                      implementáveis.

  `acceptance.md`                     Consolidará cenários de teste e
                                      validação do produto.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

**Observação:** esta especificação é uma versão inicial. As decisões
pendentes devem ser confirmadas pelo responsável pelo produto antes de
serem consideradas definitivas. Em caso de conflito, as regras aprovadas
mais recentemente deverão prevalecer e ser refletidas nos documentos
relacionados.
