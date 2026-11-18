
from .test_auth import auth_headers, login, register


def auth_client(client):
    register(client)
    token = login(client).json()["access_token"]
    return auth_headers(token)


def category_id(client, headers, name):
    categories = client.get("/api/categories", headers=headers).json()
    return next(item["id"] for item in categories if item["name"] == name)


def add(client, headers, movement_type, name, category, amount, day):
    payload = {
        "type": movement_type,
        "description": name,
        "amount": amount,
        "transaction_date": day,
        "category_id": category_id(client, headers, category),
    }
    if movement_type == "expense":
        payload["expense_type"] = (
            "fixed" if category == "Moradia (aluguel/condomínio)" else "variable"
        )
        payload["payment_method"] = "pix"
    return client.post("/api/transactions", json=payload, headers=headers)


def setup_movements(client, headers):
    # Novembro/2026
    add(client, headers, "income", "Salário", "Salário", "7000.00", "2026-11-01")
    add(
        client,
        headers,
        "expense",
        "Aluguel",
        "Moradia (aluguel/condomínio)",
        "1000.00",
        "2026-11-05",
    )
    add(client, headers, "expense", "Mercado", "Alimentação", "300.00", "2026-11-15")
    add(client, headers, "investment", "Poupança", "Poupança", "500.00", "2026-11-10")
    # Outubro/2026
    add(client, headers, "income", "Salário", "Salário", "3000.00", "2026-10-01")
    add(client, headers, "expense", "Lanches", "Alimentação", "100.00", "2026-10-20")


def test_resumo_mensal_aplica_as_formulas_aprovadas(client):
    headers = auth_client(client)
    setup_movements(client, headers)

    summary = client.get(
        "/api/dashboard/monthly", params={"month": "2026-11"}, headers=headers
    ).json()

    assert summary["total_income"] == "7000.00"
    assert summary["total_fixed_expenses"] == "1000.00"
    assert summary["total_variable_expenses"] == "300.00"
    assert summary["total_investments"] == "500.00"
    # AC-033: saídas = fixas + variáveis + investimentos.
    assert summary["total_outflows"] == "1800.00"
    # AC-025/AC-034: restante = receitas − saídas (investimentos incluídos).
    assert summary["remaining"] == "5200.00"
    assert summary["card_purchases_total"] == "0.00"


def test_itens_agrupados_e_ultimas_movimentacoes(client):
    headers = auth_client(client)
    setup_movements(client, headers)

    summary = client.get(
        "/api/dashboard/monthly", params={"month": "2026-11"}, headers=headers
    ).json()

    assert summary["income_items"] == [{"name": "Salário", "total": "7000.00"}]
    assert summary["fixed_expense_items"] == [
        {"name": "Moradia (aluguel/condomínio)", "total": "1000.00"}
    ]
    assert summary["variable_expense_items"] == [
        {"name": "Alimentação", "total": "300.00"}
    ]
    assert summary["investments_items"] == [{"name": "Poupança", "total": "500.00"}]
    assert summary["expenses_by_category"] == [
        {"name": "Alimentação", "total": "300.00"},
        {"name": "Moradia (aluguel/condomínio)", "total": "1000.00"},
    ]
    assert len(summary["recent_transactions"]) == 4
    assert summary["recent_transactions"][0]["description"] == "Mercado"


def test_trend_tem_seis_meses_com_o_mes_consultado_no_fim(client):
    headers = auth_client(client)
    setup_movements(client, headers)

    summary = client.get(
        "/api/dashboard/monthly", params={"month": "2026-11"}, headers=headers
    ).json()

    trend = summary["trend"]
    assert len(trend) == 6
    assert trend[-1]["month"] == "2026-11"
    assert trend[-1]["income"] == "7000.00"
    assert trend[-1]["expenses"] == "1300.00"
    assert trend[-2]["month"] == "2026-10"


def test_mes_sem_movimentacoes_retorna_zeros(client):
    headers = auth_client(client)

    summary = client.get(
        "/api/dashboard/monthly", params={"month": "2026-12"}, headers=headers
    ).json()

    assert summary["total_income"] == "0.00"
    assert summary["total_outflows"] == "0.00"
    assert summary["remaining"] == "0.00"
    assert summary["recent_transactions"] == []


def test_resumo_anual_retorna_12_meses_ordenados(client):
    headers = auth_client(client)
    setup_movements(client, headers)

    summary = client.get(
        "/api/dashboard/annual", params={"year": 2026}, headers=headers
    ).json()

    assert summary["year"] == 2026
    assert len(summary["months"]) == 12
    assert [item["month"] for item in summary["months"]] == [
        f"2026-{month:02d}" for month in range(1, 13)
    ]

    # AC-041: meses sem movimentação entram com zeros.
    january = summary["months"][0]
    assert january["total_income"] == "0.00"
    assert january["remaining"] == "0.00"

    november = summary["months"][10]
    assert november["total_income"] == "7000.00"
    assert november["remaining"] == "5200.00"

    assert summary["totals"]["total_income"] == "10000.00"
    assert summary["totals"]["total_expenses"] == "1400.00"
    assert summary["totals"]["total_investments"] == "500.00"
    assert summary["totals"]["final_balance"] == "8100.00"


def test_consistencia_entre_visao_mensal_e_anual(client):
    headers = auth_client(client)
    setup_movements(client, headers)

    monthly = client.get(
        "/api/dashboard/monthly", params={"month": "2026-11"}, headers=headers
    ).json()
    annual = client.get(
        "/api/dashboard/annual", params={"year": 2026}, headers=headers
    ).json()
    november = annual["months"][10]

    assert november["total_income"] == monthly["total_income"]
    assert november["total_fixed_expenses"] == monthly["total_fixed_expenses"]
    assert november["total_variable_expenses"] == monthly["total_variable_expenses"]
    assert november["total_investments"] == monthly["total_investments"]
    assert november["remaining"] == monthly["remaining"]


def test_dashboard_e_isolado_por_usuario(client):
    headers_a = auth_client(client)
    setup_movements(client, headers_a)

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    summary_b = client.get(
        "/api/dashboard/monthly", params={"month": "2026-11"}, headers=headers_b
    ).json()

    assert summary_b["total_income"] == "0.00"
    assert summary_b["remaining"] == "0.00"
    assert summary_b["recent_transactions"] == []
