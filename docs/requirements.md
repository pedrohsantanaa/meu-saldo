# requirements.md --- MeuFinanceiro

## 1. Visão geral do projeto

**Nome:** MeuSaldo --- Controle Financeiro Pessoal

O MeuSaldo será uma aplicação web minimalista para organização e
acompanhamento das finanças pessoais. A solução deverá priorizar
simplicidade, praticidade, acessibilidade e facilidade de uso, evitando
excesso de funcionalidades e complexidade.

A aplicação será acessível por navegadores em computadores, tablets e
smartphones, sem necessidade de instalação.

## 2. Problema que o sistema pretende resolver

Muitos sistemas de controle financeiro oferecem uma grande quantidade de
funcionalidades, menus e informações, tornando a experiência complexa
para usuários que desejam apenas organizar suas finanças.

O idealizador já utiliza uma planilha que atende bem às suas
necessidades, mas deseja transformar essa experiência em um sistema web,
mantendo a simplicidade e ampliando sua disponibilidade para outras
pessoas.

## 3. Objetivo geral

Desenvolver um sistema web de controle financeiro pessoal que permita
aos usuários registrar, organizar e acompanhar receitas e despesas de
maneira simples, intuitiva e centralizada.

O sistema deverá apresentar uma visão clara da situação financeira,
permitindo acompanhar o saldo, o fluxo financeiro mensal e os gastos
realizados no cartão de crédito.

## 4. Público-alvo

O sistema será destinado a pessoas que desejam organizar e controlar
suas finanças pessoais de forma simples e acessível, especialmente:

-   Pessoas que desejam controlar receitas e despesas mensais.
-   Usuários que atualmente utilizam planilhas para organizar suas
    finanças.
-   Pessoas que consideram aplicativos financeiros tradicionais
    complexos ou com excesso de funcionalidades.
-   Usuários que desejam acompanhar seus gastos e controlar o uso do
    cartão de crédito.
-   Pessoas interessadas em melhorar sua organização financeira.

## 5. Escopo do projeto

### 5.1. Escopo do MVP

A primeira versão do sistema deverá contemplar:

-   Cadastro e autenticação de usuários.
-   Registro de receitas e despesas.
-   Organização de movimentações por categorias.
-   Visualização do saldo financeiro.
-   Dashboard com resumo financeiro.
-   Controle básico de cartões de crédito.
-   Consulta de movimentações por período.
-   Interface web responsiva.

### 5.2. Funcionalidades previstas para versões futuras

Após a validação do MVP, poderão ser consideradas:

-   Relatórios financeiros mais detalhados.
-   Gráficos de evolução financeira.
-   Metas de economia.
-   Controle de despesas recorrentes.
-   Exportação de dados.
-   Recursos adicionais identificados a partir do uso e do feedback dos
    usuários.

## 6. Requisitos funcionais

  -----------------------------------------------------------------------
  ID                Requisito         Descrição         Prioridade
  ----------------- ----------------- ----------------- -----------------
  RF-01             Cadastro de       O sistema deverá  Alta
                    usuário           permitir que uma  
                                      pessoa crie uma   
                                      conta para        
                                      utilizar a        
                                      aplicação.        

  RF-02             Autenticação      O sistema deverá  Alta
                                      permitir que      
                                      usuários          
                                      cadastrados       
                                      realizem login e  
                                      logout.           

  RF-03             Cadastro de       O usuário deverá  Alta
                    receitas          poder registrar   
                                      receitas,         
                                      informando        
                                      descrição, valor, 
                                      data e categoria. 

  RF-04             Cadastro de       O usuário deverá  Alta
                    despesas          poder registrar   
                                      despesas,         
                                      informando        
                                      descrição, valor, 
                                      data e categoria. 

  RF-05             Edição e exclusão O usuário deverá  Alta
                    de movimentações  poder editar ou   
                                      excluir suas      
                                      próprias receitas 
                                      e despesas.       

  RF-06             Categorias        O sistema deverá  Alta
                                      permitir          
                                      organizar         
                                      receitas e        
                                      despesas por      
                                      categorias.       

  RF-07             Dashboard         O sistema deverá  Alta
                                      apresentar um     
                                      resumo da         
                                      situação          
                                      financeira do     
                                      usuário.          

  RF-08             Cálculo do saldo  O sistema deverá  Alta
                                      calcular o        
                                      resultado entre   
                                      receitas e        
                                      despesas no       
                                      período           
                                      selecionado.      

  RF-09             Histórico         O usuário deverá  Alta
                    financeiro        consultar         
                                      movimentações     
                                      anteriores.       

  RF-10             Filtros           O usuário deverá  Média
                                      filtrar           
                                      movimentações por 
                                      período, tipo e   
                                      categoria.        

  RF-11             Cadastro de       O usuário deverá  Alta
                    cartões           poder cadastrar   
                                      seus cartões de   
                                      crédito.          

  RF-12             Registro de       O usuário deverá  Alta
                    compras no cartão poder registrar   
                                      compras           
                                      realizadas em um  
                                      cartão            
                                      cadastrado.       

  RF-13             Controle de       O sistema deverá  Alta
                    faturas           apresentar as     
                                      compras agrupadas 
                                      por fatura,       
                                      considerando as   
                                      datas de          
                                      fechamento e      
                                      vencimento        
                                      configuradas.     

  RF-14             Acompanhamento de O sistema deverá  Média
                    limite            permitir informar 
                                      o limite do       
                                      cartão e          
                                      acompanhar o      
                                      valor             
                                      comprometido.     

  RF-15             Responsividade    A aplicação       Alta
                                      deverá adaptar    
                                      sua interface a   
                                      computadores,     
                                      tablets e         
                                      smartphones.      

  RF-16             Administração de  O administrador   Média
                    usuários          deverá poder      
                                      gerenciar contas  
                                      de usuários, sem  
                                      acesso automático 
                                      aos seus dados    
                                      financeiros       
                                      particulares.     
  -----------------------------------------------------------------------

## 7. Requisitos não funcionais

  -----------------------------------------------------------------------
  ID                      Requisito               Descrição
  ----------------------- ----------------------- -----------------------
  RNF-01                  Usabilidade             A interface deverá ser
                                                  simples, intuitiva e
                                                  exigir poucos passos
                                                  para registrar uma
                                                  movimentação.

  RNF-02                  Responsividade          O sistema deverá
                                                  funcionar adequadamente
                                                  em diferentes tamanhos
                                                  de tela.

  RNF-03                  Segurança               O sistema deverá
                                                  proteger as credenciais
                                                  e os dados financeiros
                                                  dos usuários.

  RNF-04                  Privacidade             Cada usuário deverá
                                                  acessar somente seus
                                                  próprios dados
                                                  financeiros.

  RNF-05                  Desempenho              As principais telas e
                                                  operações deverão
                                                  apresentar tempo de
                                                  resposta adequado ao
                                                  uso cotidiano.

  RNF-06                  Disponibilidade         O sistema deverá ser
                                                  disponibilizado pela
                                                  internet, por meio de
                                                  um navegador.

  RNF-07                  Manutenibilidade        O código deverá ser
                                                  organizado para
                                                  facilitar correções,
                                                  manutenção e evolução.

  RNF-08                  Compatibilidade         A aplicação deverá
                                                  funcionar nos
                                                  navegadores modernos
                                                  mais utilizados.
  -----------------------------------------------------------------------

## 8. Funcionalidades principais

### 8.1. Receitas

Permitir o registro de entradas financeiras, como salários, serviços
prestados e outros rendimentos.

Informações inicialmente previstas:

-   Descrição.
-   Valor.
-   Data de recebimento.
-   Categoria.
-   Observações opcionais.

### 8.2. Despesas

Permitir o registro de gastos realizados pelo usuário.

Informações inicialmente previstas:

-   Descrição.
-   Valor.
-   Data da despesa.
-   Categoria.
-   Forma de pagamento.
-   Observações opcionais.

### 8.3. Dashboard

A tela inicial deverá apresentar, de forma objetiva:

-   Total de receitas do mês.
-   Total de despesas do mês.
-   Saldo do período.
-   Total de gastos no cartão de crédito.
-   Últimas movimentações financeiras.
-   Resumo das despesas por categoria.

### 8.4. Saldo financeiro

O sistema deverá calcular o saldo do período a partir das receitas e
despesas registradas.

**Fórmula inicial:**

`Saldo do período = Total de receitas - Total de despesas`

A implementação deverá definir claramente como compras no cartão e
pagamentos de fatura serão tratados, evitando contabilizar a mesma
despesa duas vezes.

### 8.5. Cartão de crédito

Permitir que o usuário cadastre cartões e acompanhe as compras e
faturas.

Informações inicialmente previstas para cada cartão:

-   Nome ou identificação do cartão.
-   Limite total.
-   Dia de fechamento da fatura.
-   Dia de vencimento.
-   Compras registradas.
-   Valor da fatura atual.
-   Valor do limite disponível.

O sistema não terá integração automática com bancos ou operadoras na
primeira versão. Os dados serão informados manualmente pelo usuário.

## 9. Tipos de usuários

### 9.1. Usuário comum

Poderá:

-   Criar e gerenciar sua própria conta.
-   Cadastrar, editar e excluir receitas e despesas.
-   Gerenciar categorias.
-   Cadastrar cartões de crédito.
-   Registrar compras e consultar faturas.
-   Consultar dashboard e histórico financeiro.
-   Gerenciar suas próprias informações.

### 9.2. Administrador

Poderá:

-   Gerenciar usuários cadastrados.
-   Consultar informações administrativas do sistema.
-   Gerenciar configurações gerais.
-   Acompanhar o funcionamento da aplicação.

**Regra de privacidade:** o perfil administrativo não deverá conceder
acesso automático aos dados financeiros particulares dos usuários.

## 10. Tecnologias inicialmente previstas

As tecnologias abaixo são uma proposta inicial e poderão ser revisadas
durante a etapa de especificação e desenho da solução.

  -----------------------------------------------------------------------
  Camada                  Tecnologia              Finalidade
  ----------------------- ----------------------- -----------------------
  Front-end               Vue.js 3                Construção da interface
                                                  web.

  Estilização             Tailwind CSS            Criação de interface
                                                  minimalista e
                                                  responsiva.

  Back-end                Python + FastAPI        Desenvolvimento da API
                                                  e das regras de
                                                  negócio.

  Banco de dados          PostgreSQL              Armazenamento dos dados
                                                  da aplicação.

  Autenticação            JWT                     Autenticação e controle
                                                  de acesso.

  Versionamento           Git + GitHub            Controle de versões do
                                                  projeto.

  Hospedagem              VPS ou plataforma cloud Disponibilização do
                                                  sistema na internet.
  -----------------------------------------------------------------------

### 10.1. Arquitetura inicialmente prevista

A aplicação deverá seguir uma arquitetura cliente-servidor:

1.  **Front-end:** aplicação Vue.js responsável pela interface e
    interação com o usuário.
2.  **Back-end:** API REST desenvolvida com FastAPI, responsável pelas
    regras de negócio, validações e autenticação.
3.  **Banco de dados:** PostgreSQL, responsável pelo armazenamento
    persistente das informações.

A comunicação entre front-end e back-end será realizada por requisições
HTTP à API.

## 11. Limitações e itens fora do escopo inicial

Para manter o MVP simples e viável, não fazem parte do escopo inicial:

-   Integração automática com bancos por meio do Open Finance.
-   Conexão automática com operadoras ou instituições de cartão de
    crédito.
-   Importação automática de extratos bancários.
-   Recomendações automatizadas de investimentos.
-   Funcionalidades de contabilidade empresarial.
-   Gestão financeira compartilhada entre familiares.
-   Aplicativos nativos para Android ou iOS.
-   Realização de pagamentos, transferências ou transações bancárias.

Os lançamentos financeiros serão realizados manualmente pelos usuários.

## 12. Diretrizes de experiência do usuário

A simplicidade deverá orientar todas as decisões de interface e
desenvolvimento.

Princípios:

-   Poucos cliques para registrar uma movimentação.
-   Informações financeiras fáceis de compreender.
-   Interface limpa, sem excesso de gráficos, menus ou notificações.
-   Acesso rápido às informações mais importantes.
-   Navegação consistente e intuitiva.
-   Boa experiência tanto em computadores quanto em dispositivos móveis.
-   Controle dos dados pelo próprio usuário.

## 13. Critérios iniciais de sucesso do MVP

O MVP poderá ser considerado validado quando:

-   Um usuário conseguir criar uma conta e acessar o sistema.
-   Um usuário conseguir registrar, editar e excluir receitas e
    despesas.
-   O sistema calcular corretamente o saldo do período.
-   O dashboard apresentar os principais indicadores financeiros.
-   O usuário conseguir cadastrar um cartão e registrar compras.
-   O usuário conseguir consultar suas movimentações e faturas.
-   Os dados de um usuário não puderem ser acessados por outro usuário.
-   As principais funcionalidades puderem ser utilizadas em computador e
    smartphone.
-   Um usuário consiga realizar as operações essenciais sem depender de
    treinamento.

## 14. Princípio central do projeto

**Simplicidade acima de tudo.**

O objetivo não é criar mais um sistema financeiro cheio de
funcionalidades, mas transformar uma experiência de controle financeiro
que já funciona em uma planilha em uma aplicação web simples, organizada
e agradável de utilizar.

As três experiências prioritárias do produto são:

1.  Registrar uma movimentação em poucos segundos.
2.  Visualizar quanto entrou, quanto saiu e qual é o saldo do período.
3.  Entender os gastos e acompanhar o cartão de crédito sem complicação.

Este documento representa a definição inicial dos requisitos do projeto.
Detalhes técnicos, regras de negócio, fluxos de navegação e critérios
específicos de aceitação deverão ser aprofundados nas próximas etapas de
especificação.
