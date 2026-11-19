"""Reconciliação dos cálculos com os exemplos da planilha (T-067).

Os exemplos oficiais do responsável pelo produto estão em `spec.md` §7.4
(exemplos de contabilização aprovados em T-002/T-003) e são reproduzidos
aqui com os mesmos valores, cobrindo os cenários de reconciliação
AC-096 a AC-099. AC-100: divergências entre planilha e sistema devem ser
explicadas pelas regras definidas — as regras de período (competência da
fatura), classificação (despesa variável), fatura (consolidação única) e
duplicidade (compra × fatura) estão registradas em `spec.md` §7.2.
"""

from datetime import datetime

from .test_card_purchases import category_id
from .test_cards import auth_client, backdate_card


def create_card(client, headers, **overrides):
    payload = {
        "name": "Cartão da planilha",
        "credit_limit": "5000.00",
        "closing_day": 28,
        "due_day": 10,
    }
    payload.update(overrides)
    response = client.post("/api/cards", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def add_purchase(
    client, headers, card_id, description, amount, day, category="Alimentação"
):
    response = client.post(
        f"/api/cards/{card_id}/purchases",
        json={
            "description": description,
            "total_amount": amount,
            "purchase_date": day,
            "category_id": category_id(client, headers, category),
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def add_movement(client, headers, movement_type, description, amount, day, category):
    payload = {
        "type": movement_type,
        "description": description,
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


def monthly(client, headers, month):
    return client.get(
        "/api/dashboard/monthly", params={"month": month}, headers=headers
    ).json()


def test_exemplo_1_competencia_da_compra_no_ciclo_da_fatura(client, db_session_factory):
    """Exemplo 1 (`spec.md` §7.4, AC-098): cartão fecha dia 28 e vence dia 10.

    - Compra de R$ 150,00 em 10/11: fatura de dezembro (vence 10/12),
      conta em dezembro.
    - Compra de R$ 80,00 em 29/11: fatura de janeiro (vence 10/01),
      conta em janeiro.
    """
    headers = auth_client(client)
    card = create_card(client, headers)
    backdate_card(db_session_factory, card["id"], datetime(2026, 1, 15))
    add_purchase(
        client, headers, card["id"], "Compra de novembro", "150.00", "2026-11-10"
    )
    add_purchase(
        client, headers, card["id"], "Compra pós-fechamento", "80.00", "2026-11-29"
    )

    december = monthly(client, headers, "2026-12")
    january = monthly(client, headers, "2027-01")

    assert december["card_purchases_total"] == "150.00"
    assert january["card_purchases_total"] == "80.00"


def test_exemplo_2_pagamento_nao_duplica_a_despesa(client, db_session_factory):
    """Exemplo 2 (`spec.md` §7.4, AC-059/AC-060): a fatura de dezembro
    totaliza R$ 320,00 e é paga no vencimento; dezembro contabiliza
    R$ 320,00 uma única vez e o pagamento não altera nenhum indicador."""
    headers = auth_client(client)
    card = create_card(client, headers)
    backdate_card(db_session_factory, card["id"], datetime(2026, 1, 15))
    add_purchase(client, headers, card["id"], "Compra A", "150.00", "2026-11-10")
    add_purchase(client, headers, card["id"], "Compra B", "80.00", "2026-11-15")
    add_purchase(client, headers, card["id"], "Compra C", "90.00", "2026-11-20")

    before = monthly(client, headers, "2026-12")
    assert before["card_purchases_total"] == "320.00"
    assert before["total_variable_expenses"] == "320.00"

    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()
    client.post(
        f"/api/cards/{card['id']}/invoices/{invoices[0]['id']}/payments",
        json={"amount": "320.00", "paid_at": "2026-12-10"},
        headers=headers,
    )

    after = monthly(client, headers, "2026-12")
    assert after["card_purchases_total"] == "320.00"
    assert after["total_variable_expenses"] == "320.00"
    assert after["total_outflows"] == before["total_outflows"]
    assert after["remaining"] == before["remaining"]


def test_exemplo_3_resumo_do_mes(client, db_session_factory):
    """Exemplo 3 (`spec.md` §7.4, AC-096): receitas R$ 5.000,00; fixas
    R$ 2.000,00; variáveis R$ 800,00 (incluindo R$ 300,00 de faturas);
    investimentos R$ 400,00; saídas R$ 3.200,00; restante R$ 1.800,00."""
    headers = auth_client(client)
    card = create_card(client, headers)
    backdate_card(db_session_factory, card["id"], datetime(2026, 1, 15))
    add_movement(
        client, headers, "income", "Salário", "5000.00", "2026-12-01", "Salário"
    )
    add_movement(
        client,
        headers,
        "expense",
        "Aluguel",
        "2000.00",
        "2026-12-05",
        "Moradia (aluguel/condomínio)",
    )
    add_movement(
        client, headers, "expense", "Mercado", "500.00", "2026-12-15", "Alimentação"
    )
    add_movement(
        client, headers, "investment", "Poupança", "400.00", "2026-12-10", "Poupança"
    )
    # Compras que consolidam na fatura com vencimento em dezembro.
    add_purchase(client, headers, card["id"], "Compra A", "180.00", "2026-11-10")
    add_purchase(client, headers, card["id"], "Compra B", "120.00", "2026-11-15")

    summary = monthly(client, headers, "2026-12")

    assert summary["total_income"] == "5000.00"
    assert summary["total_fixed_expenses"] == "2000.00"
    # As variáveis incluem os R$ 300,00 de faturas de cartão.
    assert summary["total_variable_expenses"] == "800.00"
    assert summary["card_purchases_total"] == "300.00"
    assert summary["total_investments"] == "400.00"
    assert summary["total_outflows"] == "3200.00"
    assert summary["remaining"] == "1800.00"


def test_exemplo_4_orcamento_por_ciclo(client, db_session_factory):
    """Exemplo 4 (`spec.md` §7.4, AC-099): orçamento de "Alimentação" no
    cartão para dezembro: R$ 500,00; gastos de dezembro = compras da
    fatura com vencimento em dezembro (R$ 320,00); restante R$ 180,00.
    Uma compra em 29/11 entraria na fatura de janeiro e contaria no
    orçamento de janeiro."""
    headers = auth_client(client)
    card = create_card(client, headers)
    backdate_card(db_session_factory, card["id"], datetime(2026, 1, 15))
    client.post(
        "/api/budgets",
        json={
            "card_id": card["id"],
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-12",
            "budget_amount": "500.00",
        },
        headers=headers,
    )
    add_purchase(client, headers, card["id"], "Compra A", "150.00", "2026-11-10")
    add_purchase(client, headers, card["id"], "Compra B", "80.00", "2026-11-15")
    add_purchase(client, headers, card["id"], "Compra C", "90.00", "2026-11-20")
    add_purchase(
        client, headers, card["id"], "Compra de janeiro", "40.00", "2026-11-29"
    )

    december = client.get(
        "/api/budgets",
        params={"month": "2026-12", "card_id": card["id"]},
        headers=headers,
    ).json()
    january = client.get(
        "/api/budgets",
        params={"month": "2027-01", "card_id": card["id"]},
        headers=headers,
    ).json()

    assert december["rows"][0]["spent"] == "320.00"
    assert december["rows"][0]["remaining"] == "180.00"
    # A compra de 29/11 conta no orçamento de janeiro (sem orçamento lá).
    assert january["rows"][0]["spent"] == "40.00"
    assert january["rows"][0]["budget_amount"] is None


def test_visao_anual_corresponde_a_soma_dos_meses(client, db_session_factory):
    """AC-097: os valores da visão anual correspondem à soma dos meses."""
    headers = auth_client(client)
    card = create_card(client, headers)
    backdate_card(db_session_factory, card["id"], datetime(2026, 1, 15))
    add_movement(
        client, headers, "income", "Salário", "5000.00", "2026-12-01", "Salário"
    )
    add_movement(
        client, headers, "income", "Salário", "4500.00", "2026-11-01", "Salário"
    )
    add_movement(
        client,
        headers,
        "expense",
        "Aluguel",
        "2000.00",
        "2026-12-05",
        "Moradia (aluguel/condomínio)",
    )
    add_purchase(client, headers, card["id"], "Compra A", "300.00", "2026-11-10")

    annual = client.get(
        "/api/dashboard/annual", params={"year": 2026}, headers=headers
    ).json()

    months = {item["month"]: item for item in annual["months"]}
    assert months["2026-11"]["total_income"] == "4500.00"
    # A compra de 10/11 fecha em 28/11 e vence em 10/12: conta em dezembro.
    assert months["2026-11"]["total_variable_expenses"] == "0.00"
    assert months["2026-12"]["total_fixed_expenses"] == "2000.00"
    assert months["2026-12"]["total_variable_expenses"] == "300.00"
    assert annual["totals"]["total_income"] == "9500.00"
    assert annual["totals"]["total_expenses"] == "2300.00"
    assert annual["totals"]["final_balance"] == "7200.00"
