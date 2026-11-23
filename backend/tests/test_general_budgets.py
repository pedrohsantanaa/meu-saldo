"""Testes do orçamento por categoria sem cartão (T-074).

Cenários: AC-111 a AC-115 — despesas fixas e variáveis pagas fora do
cartão, com gastos derivados das movimentações comuns do mês.
"""

from .test_auth import auth_headers, login, register
from .test_card_purchases import category_id, create_purchase, setup_card
from .test_transactions import auth_client, expense_payload


def create_general_budget(client, headers, **overrides):
    payload = {
        "category_id": category_id(client, headers, "Alimentação"),
        "month": "2026-11",
        "budget_amount": "400.00",
    }
    payload.update(overrides)
    response = client.post("/api/budgets/general", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def general_summary(client, headers, month="2026-11"):
    return client.get(
        "/api/budgets/general", params={"month": month}, headers=headers
    ).json()


def create_transaction(client, headers, **overrides):
    response = client.post(
        "/api/transactions",
        json=expense_payload(client, headers, **overrides),
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def row_of(summary, name):
    return next(item for item in summary["rows"] if item["category_name"] == name)


def test_criar_orcamento_geral(client):
    headers = auth_client(client)

    body = create_general_budget(client, headers)

    # AC-111: orçamento criado para usuário + categoria + mês, sem cartão.
    assert body["budget_amount"] == "400.00"
    assert body["category_name"] == "Alimentação"
    assert body["spent"] == "0.00"
    assert body["remaining"] == "400.00"
    assert body["usage_percent"] == 0.0


def test_despesa_fixa_e_variavel_usam_o_mesmo_mecanismo(client):
    headers = auth_client(client)
    create_general_budget(
        client,
        headers,
        category_id=category_id(client, headers, "Moradia (aluguel/condomínio)"),
        budget_amount="1200.00",
    )
    create_transaction(
        client,
        headers,
        category_id=category_id(client, headers, "Moradia (aluguel/condomínio)"),
        expense_type="fixed",
        amount="1000.00",
    )

    summary = general_summary(client, headers)
    row = row_of(summary, "Moradia (aluguel/condomínio)")
    assert row["spent"] == "1000.00"
    assert row["remaining"] == "200.00"


def test_gastos_somam_movimentacoes_comuns_do_mes(client):
    headers = auth_client(client)
    create_general_budget(client, headers)
    create_transaction(client, headers, amount="120.50", transaction_date="2026-11-02")
    create_transaction(client, headers, amount="79.50", transaction_date="2026-11-30")
    # AC-112: movimentação de outubro não entra no gasto de novembro.
    create_transaction(client, headers, amount="500.00", transaction_date="2026-10-31")

    summary = general_summary(client, headers)
    row = row_of(summary, "Alimentação")
    assert row["spent"] == "200.00"
    assert row["remaining"] == "200.00"
    assert row["usage_percent"] == 50.0


def test_inclusao_e_exclusao_de_movimentacao_atualiza_o_orcamento(client):
    headers = auth_client(client)
    create_general_budget(client, headers)

    movement = create_transaction(client, headers, amount="150.00")
    assert row_of(general_summary(client, headers), "Alimentação")["spent"] == "150.00"

    client.delete(f"/api/transactions/{movement['id']}", headers=headers)
    assert row_of(general_summary(client, headers), "Alimentação")["spent"] == "0.00"


def test_categoria_sem_orcamento_como_nao_definido(client):
    headers = auth_client(client)
    create_transaction(
        client, headers, category_id=category_id(client, headers, "Lazer")
    )

    row = row_of(general_summary(client, headers), "Lazer")

    # AC-113: sem orçamento cadastrado, não se assume zero.
    assert row["budget_amount"] is None
    assert row["remaining"] is None
    assert row["usage_percent"] is None
    assert row["spent"] == "385.26"


def test_compras_no_cartao_nao_contam_no_orcamento_geral(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_general_budget(client, headers)
    create_purchase(client, headers, card["id"], total_amount="250.00")

    row = row_of(general_summary(client, headers), "Alimentação")

    # AC-114: compra no cartão segue o ciclo da fatura; nunca é movimentação
    # comum — sem dupla contagem.
    assert row["spent"] == "0.00"


def test_compra_no_cartao_nao_aparece_como_movimentacao(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"])

    movements = client.get("/api/transactions", headers=headers).json()
    assert movements == []


def test_impedir_orcamento_duplicado(client):
    headers = auth_client(client)
    create_general_budget(client, headers)

    response = client.post(
        "/api/budgets/general",
        json={
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-11",
            "budget_amount": "999.00",
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "budget_already_exists"


def test_orcamentos_do_mesmo_mes_em_categorias_diferentes(client):
    headers = auth_client(client)
    create_general_budget(client, headers)
    create_general_budget(
        client, headers, category_id=category_id(client, headers, "Lazer")
    )

    summary = general_summary(client, headers)
    assert row_of(summary, "Alimentação")["budget_amount"] == "400.00"
    assert row_of(summary, "Lazer")["budget_amount"] == "400.00"


def test_editar_e_remover_orcamento_geral(client):
    headers = auth_client(client)
    budget = create_general_budget(client, headers)

    response = client.put(
        f"/api/budgets/general/{budget['id']}",
        json={"budget_amount": "750.00"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["budget_amount"] == "750.00"

    response = client.delete(f"/api/budgets/general/{budget['id']}", headers=headers)
    assert response.status_code == 204

    # Sem orçamento e sem gasto no mês, a categoria não aparece.
    assert general_summary(client, headers)["rows"] == []


def test_percentual_somente_para_orcamento_maior_que_zero(client):
    headers = auth_client(client)
    create_general_budget(client, headers, budget_amount="0.00")
    create_transaction(client, headers, amount="10.00")

    row = row_of(general_summary(client, headers), "Alimentação")
    assert row["usage_percent"] is None
    assert row["remaining"] == "-10.00"


def test_validacoes_de_orcamento_geral(client):
    headers = auth_client(client)

    response = client.post(
        "/api/budgets/general",
        json={
            "category_id": category_id(client, headers, "Salário"),
            "month": "2026-11",
            "budget_amount": "100.00",
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "category_type_mismatch"

    response = client.post(
        "/api/budgets/general",
        json={
            "category_id": category_id(client, headers, "Poupança"),
            "month": "2026-11",
            "budget_amount": "100.00",
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "category_type_mismatch"

    response = client.post(
        "/api/budgets/general",
        json={
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-13",
            "budget_amount": "100.00",
        },
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_month"

    response = client.post(
        "/api/budgets/general",
        json={
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-11",
            "budget_amount": "-10.00",
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_categoria_inativa_nao_aceita_orcamento(client):
    headers = auth_client(client)
    lazer_id = category_id(client, headers, "Lazer")
    client.patch(
        f"/api/categories/{lazer_id}/status", json={"is_active": False}, headers=headers
    )

    response = client.post(
        "/api/budgets/general",
        json={
            "category_id": lazer_id,
            "month": "2026-11",
            "budget_amount": "100.00",
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "inactive_category"


def test_orcamentos_gerais_sao_isolados_por_usuario(client):
    headers_a = auth_client(client)
    budget = create_general_budget(client, headers_a)

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    # AC-115: a usuária B não enxerga nem edita orçamento de A.
    summary_b = general_summary(client, headers_b)
    assert summary_b["rows"] == []

    response = client.put(
        f"/api/budgets/general/{budget['id']}",
        json={"budget_amount": "999.00"},
        headers=headers_b,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "budget_not_found"

    response = client.delete(f"/api/budgets/general/{budget['id']}", headers=headers_b)
    assert response.status_code == 404
