"""Testes unitários de cálculos financeiros (T-060).

Cenários: soma de receitas, despesas fixas e variáveis, investimentos,
total de saídas e restante (`spec.md` §7.1) e orçamento menos gastos
(`spec.md` §6.13). Distribuição de parcelas não se aplica: o MVP não tem
compras parceladas (T-005).

Precisão monetária (AC-088): valores decimais somados sem erro de ponto
flutuante e quantizados em duas casas (`spec.md` §7.3).
"""

from decimal import Decimal

from app.services.budgets import row_payload
from app.services.dashboard import _money

from .test_card_purchases import category_id, create_purchase, setup_card
from .test_cards import auth_client


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


# --- Unidade: arredondamento e linhas de orçamento (spec §7.3) ------------


def test_money_quantiza_para_duas_casas_com_arredondamento_banco_centavos():
    assert _money(Decimal("10.005")) == Decimal("10.01")
    assert _money(Decimal("10.004")) == Decimal("10.00")
    assert _money(Decimal("1.10")) == Decimal("1.10")
    assert _money(None) == Decimal("0.00")


def test_linha_de_orcamento_aplica_restante_e_percentual():
    row = row_payload(
        budget_id=1,
        category_id=2,
        category_name="Gasolina",
        budget_amount=Decimal("500.00"),
        spent=Decimal("320.00"),
    )

    assert row["remaining"] == Decimal("180.00")
    assert row["usage_percent"] == 64.0


def test_linha_de_orcamento_com_restante_negativo():
    row = row_payload(
        budget_id=1,
        category_id=2,
        category_name="Gasolina",
        budget_amount=Decimal("500.00"),
        spent=Decimal("620.00"),
    )

    assert row["remaining"] == Decimal("-120.00")


# --- Integração: fórmulas aprovadas (spec §7.1) --------------------------


def test_soma_de_receitas_sem_erro_de_ponto_flutuante(client):
    headers = auth_client(client)
    # 0,10 + 0,20 com float seria 0,30000000000000004 (AC-088).
    add_movement(client, headers, "income", "Freela A", "0.10", "2026-11-05", "Salário")
    add_movement(client, headers, "income", "Freela B", "0.20", "2026-11-10", "Salário")
    add_movement(
        client, headers, "income", "Salário", "7175.09", "2026-11-01", "Salário"
    )

    summary = monthly(client, headers, "2026-11")
    assert summary["total_income"] == "7175.39"


def test_despesas_fixas_e_variaveis_sao_separadas(client):
    headers = auth_client(client)
    add_movement(
        client,
        headers,
        "expense",
        "Aluguel",
        "2000.00",
        "2026-11-05",
        "Moradia (aluguel/condomínio)",
    )
    add_movement(
        client, headers, "expense", "Mercado", "300.00", "2026-11-15", "Alimentação"
    )
    add_movement(
        client, headers, "expense", "Lanche", "200.00", "2026-11-20", "Alimentação"
    )

    summary = monthly(client, headers, "2026-11")
    assert summary["total_fixed_expenses"] == "2000.00"
    assert summary["total_variable_expenses"] == "500.00"


def test_investimentos_entram_nas_saidas_mas_nas_despesas_nao(client):
    headers = auth_client(client)
    add_movement(
        client, headers, "investment", "Poupança", "400.00", "2026-11-10", "Poupança"
    )

    summary = monthly(client, headers, "2026-11")
    assert summary["total_investments"] == "400.00"
    assert summary["total_fixed_expenses"] == "0.00"
    assert summary["total_variable_expenses"] == "0.00"


def test_total_de_saidas_e_restante(client):
    headers = auth_client(client)
    add_movement(
        client, headers, "income", "Salário", "5000.00", "2026-11-01", "Salário"
    )
    add_movement(
        client,
        headers,
        "expense",
        "Aluguel",
        "2000.00",
        "2026-11-05",
        "Moradia (aluguel/condomínio)",
    )
    add_movement(
        client, headers, "expense", "Mercado", "800.00", "2026-11-15", "Alimentação"
    )
    add_movement(
        client, headers, "investment", "Poupança", "400.00", "2026-11-10", "Poupança"
    )

    summary = monthly(client, headers, "2026-11")

    # spec §7.1: saídas = fixas + variáveis + investimentos.
    assert summary["total_outflows"] == "3200.00"
    # restante = receitas − saídas.
    assert summary["remaining"] == "1800.00"


def test_orcamento_menos_gastos(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
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
    create_purchase(client, headers, card["id"], total_amount="320.00")

    summary = client.get(
        "/api/budgets",
        params={"month": "2026-12", "card_id": card["id"]},
        headers=headers,
    ).json()
    row = summary["rows"][0]

    # spec §6.13: restante = orçamento − gastos.
    assert row["remaining"] == "180.00"
    assert summary["totals"]["remaining"] == "180.00"
