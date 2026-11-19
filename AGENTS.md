# AGENTS.md

## Repo status

- Product specs live in `docs/` (plus `docs/interface.png`, the approved prototype); the implementation plan is `docs/tasks.md` (T-001…T-073). **Fases 0–8 (T-001…T-067) are implemented** (foundation, visual identity, auth, categories, transactions, monthly/annual dashboard, credit cards/invoices/limits, budgets by card+category, test/security/usability pass); **Fase 9 remains** (production config, hosting, backups, docs). Code: `backend/` (FastAPI), `frontend/` (Vue 3 + Vite + Tailwind), `docker-compose.yml`.
- Layout: `backend/app/{api,core,models,schemas,services,repositories}`, tests in `backend/tests`, migrations in `backend/alembic`; `frontend/src/{components,layouts,pages,router,services,stores,utils}`. See `tasks.md` §4.
- Stack: Vue 3 + Tailwind + Pinia + vue-router, Python/FastAPI + SQLAlchemy 2 + Alembic, PostgreSQL 16, token auth planned (`design.md` §8.1).

## Commands

Backend (from `backend/`; local venv at `backend/.venv`):
- `pip install -r requirements-dev.txt`
- `uvicorn app.main:app --reload` — API on :8000, Swagger at `/docs`, health at `/health`
- `pytest` · `ruff check .` · `ruff format .`
- `alembic upgrade head` / `alembic downgrade base` / `alembic revision -m "..."` (reads `DATABASE_URL`; run from `backend/`)

Frontend (from `frontend/`):
- `npm install` · `npm run dev` (Vite on :5173; proxies `/api` and `/health` to the backend)
- `npm test` (Vitest) · `npm run lint` (ESLint) · `npm run format` (Prettier) · `npm run build`
- UI: shared components in `frontend/src/components` (`Base*` primitives; `SummaryCard`/`MonthSelector`/`CurrencyInput`/`EmptyState` per `design.md` §6.2) — reuse them instead of ad-hoc markup; visual tokens live in `frontend/tailwind.config.js`; charts via `chart.js` wrappers (`ChartDonut`/`ChartBars`/`ChartArea`), icons from `@heroicons/vue`. Page data loads must use `try/catch/finally` and render `LoadErrorState` (message + retry) on failure — never leave the page stuck in `LoadingState` (AC-080).

Environment: `docker compose up --build` runs postgres + backend + frontend. If host port 5432 is taken, use `POSTGRES_PORT=<free-port> docker compose up`. The backend container runs `alembic upgrade head` on start, so the DB schema tracks the code (manual: `docker compose exec backend alembic upgrade head`). Settings come from env/`.env` (see `.env.example` in each app). API errors use the standard envelope `{"error": {"code", "message", "details"}}` (`backend/app/core/errors.py`) — reuse it in new endpoints.
- Auth: `POST /api/auth/register|login|logout`, `GET /api/auth/me`. Private routes must depend on `get_current_user` (`backend/app/api/deps.py`) — it is the **only** source of user scoping (data isolation). Tokens are JWT bound to revocable `auth_sessions` rows (logout revokes immediately). Tests run against in-memory SQLite (no Postgres needed).
- Financial data: `GET/POST/PUT /api/categories` + `PATCH /api/categories/{id}/status`; `GET/POST/PUT/DELETE /api/transactions`. All queries are scoped by the authenticated user (other users' records → 404). Registering a user seeds the 27 default categories as per-user editable copies (`app/services/seed.py`). Expenses require `expense_type` (fixed/variable) and `payment_method` (dinheiro/pix/debito/outra — **there is no "credito"**: card spending is registered as a card purchase, never as a common transaction).
- Credit cards (Fase 6): `GET/POST /api/cards`, `GET/PUT /api/cards/{id}`, `PATCH /api/cards/{id}/status` (inactivate, never delete); `GET/POST /api/cards/{id}/purchases` + `GET/PUT/DELETE .../purchases/{pid}`; `GET /api/cards/{id}/invoices` (+ `/invoices/overview`, `/invoices/{iid}`); `POST /api/cards/{id}/invoices/{iid}/payments`. Invoice assignment is a **snapshot** at purchase registration (`app/services/invoice_cycle.py`); the invoice total is derived from its purchases (never materialized); paying an invoice settles it (never creates a `Transaction`) and releases the limit. Cards have a user-chosen `color` token (19-color palette enum in `app/schemas/credit_card.py`; gradient map in `frontend/src/utils/cardColors.js`; picked via `ColorPicker.vue` — legacy cards fall back to the id-based gradient).
- Budgets (Fase 7): `GET /api/budgets?month=AAAA-MM&card_id=` (rows + totals; categories without budget come as `budget_amount: null` = "Não definido"), `POST /api/budgets`, `PUT/DELETE /api/budgets/{id}` (`app/services/budgets.py`). Spending is always derived from purchases on the invoice due in the month — never materialized; "próximo do limite" threshold is **80%** (approved in Fase 7, `NEAR_LIMIT_PERCENT` in `frontend/src/utils/budget.js`).
- Dashboard: `GET /api/dashboard/monthly?month=AAAA-MM` and `/api/dashboard/annual?year=AAAA` (`app/services/dashboard.py`). Formulas follow `spec.md` §7.1: `saídas = fixas + variáveis + investimentos`, `restante = receitas − saídas`; monetary values are quantized to 2 decimals. Monthly and annual views must stay consistent.

## Documents (all in Portuguese, pt-BR)

| File | Role |
|---|---|
| `docs/requirements.md` | Problem, audience, scope, RF/RNF requirements |
| `docs/spec.md` | Feature behavior, business rules, acceptance criteria (incl. DP-01…DP-09 pending decisions) |
| `docs/design.md` | UI/UX, architecture, data model, proposed API (incl. DD-01…DD-10 pending decisions) |
| `docs/tasks.md` | Implementation tasks (T-xxx), priorities, phases, Definition of Done |
| `docs/acceptance.md` | Test scenarios (AC-xxx) in **Dado / Quando / Então** format |

**Conflict rule (explicit in `acceptance.md` §2):** later product-owner decisions recorded in `tasks.md`/`acceptance.md` override older text. Known case (already reconciled in T-001): the annual overview **is** in planned scope and `design.md` §2.1 was corrected accordingly. Divergence register: `spec.md` §15.

Keep doc edits in Portuguese and in character style consistent with the existing files.

## Domain rules that are easy to get wrong

- **Card accounting policy (confirmed in T-002, `spec.md` §7.2 + examples §7.4):** regular movements (income/expense/investment) count in the month of their own date. **Card purchases count in the month of the invoice cycle they belong to; the invoice is identified by its due-date month** ("January invoice" = the one due in January). Cycle membership is computed from the card's configured closing day (collected at card registration, `spec.md` §6.8); purchases after closing fall into the next cycle. The invoice total is counted **once** as a variable expense in the month of its due date; individual purchases are detail only (Cards/Budgets screens) and are never summed again; paying an invoice is *settlement of an obligation*, never a new consumption expense. Budgets follow the same invoice cycle (T-003). See AC-059/AC-060/AC-101/AC-102.
- **Invoice cycle rules (T-004, `spec.md` §6.10):** purchases made exactly on the closing day go to the **next** cycle; when a configured closing/due day does not exist in a month, use the month's last day; a card's first invoice runs from card creation until the day before the next closing.
- **No installments in the MVP (T-005)** — purchases are single-payment only; `CreditCardInstallment` stays unused (`design.md` §9.1).
- **Card limit (T-006, `spec.md` §6.11):** `available = total − committed`; committed = purchases on unpaid invoices minus registered payments. Invoice payment (settlement, never a new expense) **releases** the limit: full payment frees the whole invoice, partial frees the paid amount.
- **Fixed expenses are entered manually each month (T-007)** — no automatic recurrence in the MVP.
- **Categories are fully editable (T-008, `spec.md` §6.3)** — including system defaults (create/rename/deactivate/reactivate); default seed list in `spec.md` §6.3 (income / fixed expenses / variable expenses / investments).
- **Money is decimal**, never float; two decimal places; display as `R$ 1.234,56`. Installments must sum exactly to the purchase total (cent differences handled) (`spec.md` §7.3).
- **Budget key is `user + card + month + category`** and must be unique; budget is per-card, and the same category can have different limits on different cards. A missing budget shows "Não definido" — never assume zero (`design.md` §5.4, AC-065/AC-072). Usage states (T-058): `undefined`/`ok`/`near` (≥ 80%)/`full`/`over`; percentage is only calculated for budget > 0.
- **Multiple credit cards** per user; a card that is inactive keeps its history but accepts no new purchases.
- **Monthly + annual overview** are both planned (reconciled in T-001; `design.md` §2.1 corrected): monthly = one month with navigation; annual = 12 months in columns.
- **Every private record belongs to one user**; all queries/actions must filter by the authenticated user, enforced in the back-end, not just the UI. Admin role must **not** grant access to users' financial data.
- **Never store full card numbers, CVV, or bank credentials** — not even in tests/fixtures.

## Pending decisions

- Specs contain items marked **"Pendente de definição"** — they are **not** rules: do not implement behavior that depends on them without a product-owner decision (`tasks.md` §1). Fase 0 (T-001…T-008) resolved DP-02…DP-07 and DD-01…DD-08 (plus DP-04/DD-02 in T-002); **DP-08** (password recovery) was approved and implemented in T-026; Fase 7 resolved **DD-10** (missing budget shows "Não definido") and the **"próximo do limite" threshold (80%)**. **Still pending:** DP-01 (shared accounts — out of MVP), DP-09 (data export — future), and DD-09 (investment goals).

## Conventions in the docs

- Task markers: `[ ]` pending, `[x]` done, `[!]` blocked; priorities **P0** (MVP-essential) / P1 / P2. A task is done only when code is implemented, reviewed and tested (`tasks.md` §3).
- Acceptance items are `AC-xxx [P0|P1|Condicional]` scenarios; a feature is accepted only when its applicable ACs pass and no known failures affect calculations, privacy, or data integrity (`acceptance.md` §1).
- Source of functional truth is the product owner's spreadsheets: the app must preserve their logic (income sources, fixed/variable expenses, investments counted in "restante", per-card budgets) — `design.md` §1 and `docs/interface.png`.
- **Visual source of truth is `docs/interface.png`** (approved prototype): dark navy sidebar with blue active states, green primary actions, purple=investments, orange=variable expenses, icon badges on indicator cards. Navigation follows the prototype: Dashboard (Visão Mensal `/` + Visão Anual `/anual`), Movimentações, Cartões, Orçamentos, Categorias, Relatórios, Configurações (`spec.md` §8.2, AC-077 updated). Demo screens reuse the prototype's sample data.
- "Restante" is the result of registered entries (`receitas − saídas`, where `saídas = fixas + variáveis + investimentos`), **not** a real bank balance (`design.md` §11.1).

## Windows gotcha

The `.md` files are **UTF-8 without BOM** with accented pt-BR text. PowerShell 5.1 `Get-Content`/`Out-File` and `type` default to the system ANSI code page and will show or write mojibake — read/write these files with UTF-8-aware tools (or pass `-Encoding utf8`) to avoid corrupting them.
