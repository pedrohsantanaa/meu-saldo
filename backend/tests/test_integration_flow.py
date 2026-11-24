"""Testes de integração da API (T-063).

Fluxo completo ponta a ponta: cadastro e autenticação, categorias e
movimentações, dashboard mensal e anual, cartões/compras/faturas e
orçamentos — verificando a consistência dos indicadores após cada etapa
(AC-090).
"""

from .test_auth import auth_headers, login
from .test_card_purchases import category_id
from .test_cards import auth_client


def test_fluxo_completo_do_usuario(client, db_session_factory):
    # --- Cadastro e autenticação (T-021 a T-025) ------------------------
    headers = auth_client(client)
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "ana@example.com"

    # --- Categorias (T-027): seed de 27 categorias do usuário ----------
    categories = client.get("/api/categories", headers=headers).json()
    assert len(categories) == 27

    # --- Movimentações (T-029 a T-033) ---------------------------------
    for payload in (
        {
            "type": "income",
            "description": "Salário",
            "amount": "5000.00",
            "transaction_date": "2026-11-01",
            "category_id": category_id(client, headers, "Salário"),
        },
        {
            "type": "expense",
            "description": "Aluguel",
            "amount": "2000.00",
            "transaction_date": "2026-11-05",
            "category_id": category_id(client, headers, "Moradia (aluguel/condomínio)"),
            "expense_type": "fixed",
            "payment_method": "pix",
        },
        {
            "type": "expense",
            "description": "Mercado",
            "amount": "500.00",
            "transaction_date": "2026-11-15",
            "category_id": category_id(client, headers, "Alimentação"),
            "expense_type": "variable",
            "payment_method": "debito",
        },
        {
            "type": "investment",
            "description": "Poupança",
            "amount": "400.00",
            "transaction_date": "2026-11-10",
            "category_id": category_id(client, headers, "Poupança"),
        },
    ):
        created = client.post("/api/transactions", json=payload, headers=headers)
        assert created.status_code == 201

    listing = client.get("/api/transactions", headers=headers).json()
    assert len(listing) == 4

    # --- Cartões, compras e faturas (Fase 6) ---------------------------
    card = client.post(
        "/api/cards",
        json={
            "name": "Nubank",
            "credit_limit": "5000.00",
            "closing_day": 28,
            "due_day": 10,
        },
        headers=headers,
    ).json()
    purchase = client.post(
        f"/api/cards/{card['id']}/purchases",
        json={
            "description": "Supermercado no cartão",
            "total_amount": "300.00",
            "purchase_date": "2026-11-10",
            "category_id": category_id(client, headers, "Alimentação"),
        },
        headers=headers,
    )
    assert purchase.status_code == 201

    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()
    assert len(invoices) == 1
    assert invoices[0]["due_date"] == "2026-12-10"
    assert invoices[0]["total"] == "300.00"

    # --- Dashboard (T-035/T-039) --------------------------------------
    december = client.get(
        "/api/dashboard/monthly", params={"month": "2026-12"}, headers=headers
    ).json()
    assert december["card_purchases_total"] == "300.00"
    assert december["total_variable_expenses"] == "300.00"

    november = client.get(
        "/api/dashboard/monthly", params={"month": "2026-11"}, headers=headers
    ).json()
    assert november["total_income"] == "5000.00"
    assert november["total_fixed_expenses"] == "2000.00"
    assert november["total_variable_expenses"] == "500.00"
    assert november["total_investments"] == "400.00"
    assert november["total_outflows"] == "2900.00"
    assert november["remaining"] == "2100.00"

    annual = client.get(
        "/api/dashboard/annual", params={"year": 2026}, headers=headers
    ).json()
    assert annual["months"][11]["total_variable_expenses"] == "300.00"
    assert annual["totals"]["total_income"] == "5000.00"

    # --- Pagamento de fatura (T-051) ----------------------------------
    payment = client.post(
        f"/api/cards/{card['id']}/invoices/{invoices[0]['id']}/payments",
        json={"amount": "300.00", "paid_at": "2026-12-10"},
        headers=headers,
    )
    assert payment.status_code == 201

    card_after = client.get(f"/api/cards/{card['id']}", headers=headers).json()
    assert card_after["committed_amount"] == "0.00"
    assert card_after["available_limit"] == "5000.00"

    # --- Orçamentos (Fase 7) ------------------------------------------
    # O abatimento segue o mês da compra (10/11), não o da fatura.
    budget = client.post(
        "/api/budgets",
        json={
            "card_id": card["id"],
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-11",
            "budget_amount": "500.00",
        },
        headers=headers,
    )
    assert budget.status_code == 201

    summary = client.get(
        "/api/budgets",
        params={"month": "2026-11", "card_id": card["id"]},
        headers=headers,
    ).json()
    assert summary["rows"][0]["spent"] == "300.00"
    assert summary["rows"][0]["remaining"] == "200.00"

    # --- Consistência após alteração (AC-090) -------------------------
    client.put(
        f"/api/cards/{card['id']}/purchases/{purchase.json()['id']}",
        json={"total_amount": "450.00"},
        headers=headers,
    )
    summary = client.get(
        "/api/budgets",
        params={"month": "2026-11", "card_id": card["id"]},
        headers=headers,
    ).json()
    december = client.get(
        "/api/dashboard/monthly", params={"month": "2026-12"}, headers=headers
    ).json()
    assert summary["rows"][0]["spent"] == "450.00"
    assert summary["rows"][0]["remaining"] == "50.00"
    assert december["card_purchases_total"] == "450.00"

    # Logout revoga a sessão imediatamente (T-023).
    client.post("/api/auth/logout", headers=headers)
    after_logout = client.get("/api/auth/me", headers=headers)
    assert after_logout.status_code == 401


def test_validacao_no_servidor_rejeita_dados_invalidos(client):
    # AC-087: a API valida mesmo quando chamada fora da interface.
    headers = auth_client(client)

    response = client.post(
        "/api/transactions",
        json={
            "type": "expense",
            "description": "",
            "amount": "-5.00",
            "transaction_date": "2026-11-15",
            "category_id": 99999,
        },
        headers=headers,
    )
    assert response.status_code == 422

    response = client.post(
        "/api/cards",
        json={"name": "X", "credit_limit": "abc", "closing_day": 40, "due_day": 0},
        headers=headers,
    )
    assert response.status_code == 422

    response = client.post(
        "/api/budgets",
        json={
            "card_id": 1,
            "category_id": 1,
            "month": "invalido",
            "budget_amount": "10.00",
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_segunda_sessao_do_mesmo_usuario_enxerga_os_mesmos_dados(client):
    headers_a = auth_client(client)
    client.post(
        "/api/cards",
        json={
            "name": "Nubank",
            "credit_limit": "5000.00",
            "closing_day": 28,
            "due_day": 10,
        },
        headers=headers_a,
    )

    # Nova sessão (novo token) para o mesmo usuário.
    headers_b = auth_headers(login(client).json()["access_token"])
    listing = client.get("/api/cards", headers=headers_b).json()

    assert len(listing) == 1
    assert listing[0]["name"] == "Nubank"
