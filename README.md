# meuSaldo

Aplicação web de controle financeiro pessoal: receitas, despesas, investimentos,
cartões de crédito, faturas e orçamentos por categoria — com simplicidade como
princípio central.

Este repositório contém a documentação do produto (`docs/`) e a estrutura inicial
do código (Fase 1 do plano de implementação).

## Estrutura

```text
meu-saldo/
├── docs/                  # Especificações do produto (requirements, spec, design, tasks, acceptance)
├── backend/               # API Python (FastAPI)
│   ├── app/               # api/, core/, models/, schemas/, services/, repositories/
│   ├── tests/             # Testes automatizados (pytest)
│   ├── alembic/           # Migrações do banco
│   ├── requirements.txt   # Dependências de execução
│   └── requirements-dev.txt
├── frontend/              # Interface (Vue 3 + Vite + Tailwind CSS)
│   └── src/               # components/, layouts/, pages/, router/, services/, stores/, utils/
└── docker-compose.yml     # Ambiente local (postgres + backend + frontend)
```

## Pré-requisitos

- Python 3.12+
- Node.js 22+ e npm
- Docker e Docker Compose (para o banco e para o ambiente completo)

## Como executar

### Opção 1 — Docker Compose (recomendado)

```bash
docker compose up --build
```

- Front-end: <http://localhost:5173>
- Back-end (Swagger): <http://localhost:38000/docs>
- Saúde da API: <http://localhost:38000/health>
- PostgreSQL: `localhost:15432` (banco/usuário/senha `meusaldo` por padrão;
  portas configuráveis no `docker-compose.yml`)

Ao encerrar: `docker compose down` (use `docker compose down -v` para remover os dados).

### Opção 2 — Execução manual

Banco (pode ser o serviço isolado do Compose):

```bash
docker compose up -d db
```

Back-end:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # ajuste se necessário
uvicorn app.main:app --reload
```

Front-end:

```bash
cd frontend
npm install
npm run dev
```

## Migrações do banco (Alembic)

Executam a partir da pasta `backend/`, lendo `DATABASE_URL` do ambiente ou de `.env`:

```bash
alembic upgrade head      # aplica todas as migrações
alembic downgrade base    # reverte tudo
alembic revision -m "descricao"   # cria uma nova migração
```

A primeira revisão (`0001_baseline`) é intencionalmente vazia; as entidades
serão adicionadas nas próximas fases do plano (`docs/tasks.md`).

## Qualidade e testes

Back-end:

```bash
cd backend
ruff check .              # lint
ruff format .             # formatação
pytest                    # testes
```

Front-end:

```bash
cd frontend
npm run lint              # ESLint
npm run format            # Prettier
npm test                  # Vitest
npm run build             # build de produção
```

Erros da API seguem o envelope padronizado
`{"error": {"code", "message", "details"}}` (`backend/app/core/errors.py`).

## Documentação do produto

Antes de alterar regras de negócio, leia os documentos em `docs/` —
especialmente as regras de contabilização (`spec.md` §7) e as decisões
pendentes (`spec.md` §12 e `design.md` §15). O plano de trabalho está em
`docs/tasks.md` e os critérios de aceitação em `docs/acceptance.md`.
