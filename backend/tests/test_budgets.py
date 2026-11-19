"""Testes de orçamentos por cartão e categoria (T-053 a T-058).

Cenários: AC-063 a AC-075.
"""

from .test_auth import auth_headers, login, register
from .test_card_purchases import category_id, create_purchase, setup_card
from .test_cards import auth_client


def create_budget(client, headers, card_id, **overrides):
    payload = {
        "card_id": card_id,
        "category_id": category_id(client, headers, "Alimentação"),
        "month": "2026-12",
        "budget_amount": "500.00",
    }
    payload.update(overrides)
    response = client.post("/api/budgets", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def budget_summary(client, headers, card_id, month="2026-12"):
    return client.get(
        "/api/budgets",
        params={"month": month, "card_id": card_id},
        headers=headers,
    ).json()


def row_of(summary, name):
    return next(item for item in summary["rows"] if item["category_name"] == name)


def test_criar_orcamento(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    body = create_budget(client, headers, card["id"])

    # AC-064: orçamento criado para usuário + cartão + mês + categoria.
    assert body["budget_amount"] == "500.00"
    assert body["category_name"] == "Alimentação"
    assert body["spent"] == "0.00"
    assert body["remaining"] == "500.00"
    assert body["usage_percent"] == 0.0


def test_impedir_orcamento_duplicado(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"])

    response = client.post(
        "/api/budgets",
        json={
            "card_id": card["id"],
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-12",
            "budget_amount": "300.00",
        },
        headers=headers,
    )

    # AC-065: a combinação é única; o usuário é direcionado a editar.
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "budget_already_exists"


def test_orcamentos_independentes_por_cartao(client, db_session_factory):
    headers = auth_client(client)
    card_a = setup_card(client, headers, db_session_factory, name="Cartão A")
    card_b = setup_card(client, headers, db_session_factory, name="Cartão B")
    create_budget(client, headers, card_a["id"], budget_amount="500.00")
    create_budget(client, headers, card_b["id"], budget_amount="800.00")

    # AC-066: mesma categoria em cartões diferentes tem valores próprios.
    summary_a = budget_summary(client, headers, card_a["id"])
    summary_b = budget_summary(client, headers, card_b["id"])
    assert row_of(summary_a, "Alimentação")["budget_amount"] == "500.00"
    assert row_of(summary_b, "Alimentação")["budget_amount"] == "800.00"

    # E o mesmo vale para meses diferentes.
    create_budget(
        client, headers, card_a["id"], month="2027-01", budget_amount="100.00"
    )
    summary_jan = budget_summary(client, headers, card_a["id"], month="2027-01")
    assert row_of(summary_jan, "Alimentação")["budget_amount"] == "100.00"


def test_gastos_seguem_o_ciclo_da_fatura(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"])
    # Compra em 10/11: fatura de dezembro (vence 10/12).
    create_purchase(client, headers, card["id"], total_amount="150.00")
    # Compra em 29/11: fatura de janeiro (vence 10/01).
    create_purchase(
        client,
        headers,
        card["id"],
        description="Compra de janeiro",
        total_amount="80.00",
        purchase_date="2026-11-29",
    )

    # AC-067: só conta a compra atribuída à fatura do mês.
    december = row_of(budget_summary(client, headers, card["id"]), "Alimentação")
    january = row_of(
        budget_summary(client, headers, card["id"], month="2027-01"), "Alimentação"
    )
    assert december["spent"] == "150.00"
    assert january["spent"] == "80.00"


def test_calcular_restante(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"], budget_amount="500.00")
    create_purchase(client, headers, card["id"], total_amount="320.00")

    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")

    # AC-068: restante = orçamento − gastos.
    assert row["remaining"] == "180.00"
    assert row["usage_percent"] == 64.0


def test_orcamento_nao_utilizado(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"], budget_amount="500.00")

    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")

    # AC-069: sem compras, gastos R$ 0,00 e restante = orçamento.
    assert row["spent"] == "0.00"
    assert row["remaining"] == "500.00"


def test_orcamento_totalmente_utilizado(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"], budget_amount="500.00")
    create_purchase(client, headers, card["id"], total_amount="500.00")

    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")

    # AC-070: restante R$ 0,00 quando gastos = orçamento.
    assert row["spent"] == "500.00"
    assert row["remaining"] == "0.00"
    assert row["usage_percent"] == 100.0


def test_orcamento_ultrapassado(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"], budget_amount="500.00")
    create_purchase(client, headers, card["id"], total_amount="620.00")

    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")

    # AC-071: restante negativo quando os gastos superam o orçamento.
    assert row["remaining"] == "-120.00"
    assert row["usage_percent"] == 124.0


def test_categoria_sem_orcamento_como_nao_definido(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"], total_amount="150.00")

    summary = budget_summary(client, headers, card["id"])
    row = row_of(summary, "Alimentação")

    # AC-072: "Não definido" — sem assumir zero e sem percentual.
    assert row["id"] is None
    assert row["budget_amount"] is None
    assert row["remaining"] is None
    assert row["usage_percent"] is None
    assert row["spent"] == "150.00"


def test_editar_e_remover_orcamento(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    budget = create_budget(client, headers, card["id"], budget_amount="500.00")
    create_purchase(client, headers, card["id"], total_amount="150.00")

    edited = client.put(
        f"/api/budgets/{budget['id']}",
        json={"budget_amount": "700.00"},
        headers=headers,
    )
    assert edited.status_code == 200
    assert edited.json()["budget_amount"] == "700.00"
    assert edited.json()["remaining"] == "550.00"

    removed = client.delete(f"/api/budgets/{budget['id']}", headers=headers)

    # AC-073: remover o orçamento não exclui as compras.
    assert removed.status_code == 204
    summary = budget_summary(client, headers, card["id"])
    row = row_of(summary, "Alimentação")
    assert row["budget_amount"] is None
    assert row["spent"] == "150.00"
    purchases = client.get(f"/api/cards/{card['id']}/purchases", headers=headers).json()
    assert len(purchases) == 1


def test_atualiza_orcamento_apos_compra(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"], budget_amount="500.00")
    purchase = create_purchase(client, headers, card["id"], total_amount="150.00")

    # AC-074: inclusão.
    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")
    assert row["spent"] == "150.00"

    # Edição.
    client.put(
        f"/api/cards/{card['id']}/purchases/{purchase['id']}",
        json={"total_amount": "250.00"},
        headers=headers,
    )
    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")
    assert row["spent"] == "250.00"

    # Exclusão.
    client.delete(
        f"/api/cards/{card['id']}/purchases/{purchase['id']}", headers=headers
    )
    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")
    assert row["spent"] == "0.00"


def test_totalizador_respeita_categorias_sem_orcamento(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"], budget_amount="500.00")
    create_purchase(client, headers, card["id"], total_amount="150.00")
    # Compra em categoria sem orçamento.
    create_purchase(
        client,
        headers,
        card["id"],
        description="Gasolina",
        total_amount="80.00",
        category_id=category_id(client, headers, "Transporte/combustível"),
    )

    summary = budget_summary(client, headers, card["id"])

    # AC-075: totalizadores somam as linhas exibidas.
    assert summary["totals"]["budget_amount"] == "500.00"
    assert summary["totals"]["spent"] == "230.00"
    # Restante soma apenas as categorias com orçamento definido.
    assert summary["totals"]["remaining"] == "350.00"


def test_percentual_somente_para_orcamento_maior_que_zero(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"], budget_amount="0.00")

    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")

    # T-058: orçamento zero não tem percentual.
    assert row["usage_percent"] is None


def test_pagamento_de_fatura_nao_entra_nos_gastos(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_budget(client, headers, card["id"], budget_amount="500.00")
    create_purchase(client, headers, card["id"], total_amount="150.00")

    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()
    client.post(
        f"/api/cards/{card['id']}/invoices/{invoices[0]['id']}/payments",
        json={"amount": "150.00", "paid_at": "2026-12-10"},
        headers=headers,
    )

    # T-057: o pagamento liquidia a fatura e não é uma compra.
    row = row_of(budget_summary(client, headers, card["id"]), "Alimentação")
    assert row["spent"] == "150.00"


def test_validacoes_de_orcamento(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    # Valor negativo é rejeitado.
    response = client.post(
        "/api/budgets",
        json={
            "card_id": card["id"],
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-12",
            "budget_amount": "-1.00",
        },
        headers=headers,
    )
    assert response.status_code == 422

    # Categoria de investimento é incompatível.
    response = client.post(
        "/api/budgets",
        json={
            "card_id": card["id"],
            "category_id": category_id(client, headers, "Poupança"),
            "month": "2026-12",
            "budget_amount": "100.00",
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "category_type_mismatch"

    # Cartão de outro usuário (inexistente para este usuário).
    response = client.post(
        "/api/budgets",
        json={
            "card_id": card["id"] + 999,
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-12",
            "budget_amount": "100.00",
        },
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "card_not_found"


def test_orcamentos_sao_isolados_por_usuario(client, db_session_factory):
    headers_a = auth_client(client)
    card = setup_card(client, headers_a, db_session_factory)
    budget = create_budget(client, headers_a, card["id"])

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    summary_b = client.get(
        "/api/budgets",
        params={"month": "2026-12", "card_id": card["id"]},
        headers=headers_b,
    )
    assert summary_b.status_code == 404
    assert summary_b.json()["error"]["code"] == "card_not_found"

    response = client.put(
        f"/api/budgets/{budget['id']}",
        json={"budget_amount": "999.00"},
        headers=headers_b,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "budget_not_found"

    response = client.delete(f"/api/budgets/{budget['id']}", headers=headers_b)
    assert response.status_code == 404
