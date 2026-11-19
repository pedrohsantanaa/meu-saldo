"""Testes de faturas, limite e pagamento (T-049, T-050, T-051).

Cenários: AC-052, AC-056, AC-058, AC-060, AC-062 e AC-106.
"""

from .test_auth import auth_headers, login, register
from .test_card_purchases import create_purchase, setup_card
from .test_cards import auth_client


def invoice_id_of(client, headers, card_id, reference_month):
    invoices = client.get(f"/api/cards/{card_id}/invoices", headers=headers).json()
    return next(
        item["id"] for item in invoices if item["reference_month"] == reference_month
    )


def test_total_da_fatura_e_a_soma_das_compras(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"], total_amount="150.00")
    create_purchase(
        client,
        headers,
        card["id"],
        description="Lanche",
        total_amount="58.88",
        purchase_date="2026-11-15",
    )

    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()

    # AC-056: o total corresponde à soma das compras da fatura.
    assert len(invoices) == 1
    assert invoices[0]["total"] == "208.88"
    assert invoices[0]["open_amount"] == "208.88"
    assert invoices[0]["status"] == "open"


def test_historico_de_faturas_por_ciclo(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"], purchase_date="2026-11-10")
    create_purchase(
        client,
        headers,
        card["id"],
        description="Compra de dezembro",
        total_amount="80.00",
        purchase_date="2026-11-29",
    )

    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()

    # AC-058: ciclos diferentes aparecem com datas e totais.
    assert [(item["reference_month"], item["total"]) for item in invoices] == [
        ("2027-01-01", "80.00"),
        ("2026-12-01", "150.00"),
    ]
    assert [item["due_date"] for item in invoices] == ["2027-01-10", "2026-12-10"]


def test_visao_atual_e_proxima_fatura(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"], purchase_date="2026-11-10")
    create_purchase(
        client,
        headers,
        card["id"],
        description="Compra de dezembro",
        total_amount="80.00",
        purchase_date="2026-11-29",
    )

    overview = client.get(
        f"/api/cards/{card['id']}/invoices/overview", headers=headers
    ).json()

    # AC-052: fatura atual (em aberto) e próxima fatura.
    assert overview["current"]["reference_month"] == "2026-12-01"
    assert overview["current"]["total"] == "150.00"
    assert overview["next"]["reference_month"] == "2027-01-01"


def test_pagamento_parcial_libera_limite_parcialmente(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory, credit_limit="5000.00")
    create_purchase(client, headers, card["id"], total_amount="1000.00")
    invoice_id = invoice_id_of(client, headers, card["id"], "2026-12-01")

    committed_before = client.get(f"/api/cards/{card['id']}", headers=headers).json()
    assert committed_before["committed_amount"] == "1000.00"
    assert committed_before["available_limit"] == "4000.00"

    response = client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "400.00", "paid_at": "2026-12-10"},
        headers=headers,
    )

    # AC-062/AC-106: pagamento parcial libera o valor pago.
    assert response.status_code == 201
    card_after = client.get(f"/api/cards/{card['id']}", headers=headers).json()
    assert card_after["committed_amount"] == "600.00"
    assert card_after["available_limit"] == "4400.00"

    invoice = client.get(
        f"/api/cards/{card['id']}/invoices/{invoice_id}", headers=headers
    ).json()
    assert invoice["status"] == "partial"
    assert invoice["paid_amount"] == "400.00"
    assert invoice["open_amount"] == "600.00"


def test_pagamento_total_libera_todo_o_limite(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory, credit_limit="5000.00")
    create_purchase(client, headers, card["id"], total_amount="1000.00")
    invoice_id = invoice_id_of(client, headers, card["id"], "2026-12-01")

    client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "1000.00", "paid_at": "2026-12-10"},
        headers=headers,
    )

    # AC-106: pagamento total libera toda a fatura.
    card_after = client.get(f"/api/cards/{card['id']}", headers=headers).json()
    assert card_after["committed_amount"] == "0.00"
    assert card_after["available_limit"] == "5000.00"

    invoice = client.get(
        f"/api/cards/{card['id']}/invoices/{invoice_id}", headers=headers
    ).json()
    assert invoice["status"] == "paid"


def test_pagamento_nao_e_nova_despesa_de_consumo(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"], total_amount="300.00")
    invoice_id = invoice_id_of(client, headers, card["id"], "2026-12-01")

    client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "300.00", "paid_at": "2026-12-10"},
        headers=headers,
    )

    # AC-060: o pagamento liquida a obrigação e não vira movimentação.
    transactions = client.get("/api/transactions", headers=headers).json()
    assert transactions == []


def test_pagamento_nao_pode_exceder_o_saldo_aberto(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"], total_amount="300.00")
    invoice_id = invoice_id_of(client, headers, card["id"], "2026-12-01")

    response = client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "400.00", "paid_at": "2026-12-10"},
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "payment_exceeds_open_balance"


def test_nao_paga_fatura_ja_liquidada(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"], total_amount="300.00")
    invoice_id = invoice_id_of(client, headers, card["id"], "2026-12-01")
    client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "300.00", "paid_at": "2026-12-10"},
        headers=headers,
    )

    response = client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "10.00", "paid_at": "2026-12-11"},
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invoice_already_paid"


def test_detalhe_da_fatura_inclui_compras_e_pagamentos(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    create_purchase(client, headers, card["id"], total_amount="300.00")
    invoice_id = invoice_id_of(client, headers, card["id"], "2026-12-01")
    client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "100.00", "paid_at": "2026-12-05"},
        headers=headers,
    )

    invoice = client.get(
        f"/api/cards/{card['id']}/invoices/{invoice_id}", headers=headers
    ).json()

    assert len(invoice["purchases"]) == 1
    assert invoice["purchases"][0]["total_amount"] == "300.00"
    assert len(invoice["payments"]) == 1
    assert invoice["payments"][0]["amount"] == "100.00"


def test_edicao_de_compra_recalcula_indicadores_apos_pagamento(
    client, db_session_factory
):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory, credit_limit="1000.00")
    purchase = create_purchase(client, headers, card["id"], total_amount="500.00")
    invoice_id = invoice_id_of(client, headers, card["id"], "2026-12-01")
    client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "500.00", "paid_at": "2026-12-10"},
        headers=headers,
    )

    # AC-057: edição recalcula fatura e indicadores; pagamento não é
    # despesa — o limite volta a comprometer apenas a diferença.
    client.put(
        f"/api/cards/{card['id']}/purchases/{purchase['id']}",
        json={"total_amount": "700.00"},
        headers=headers,
    )

    card_after = client.get(f"/api/cards/{card['id']}", headers=headers).json()
    assert card_after["committed_amount"] == "200.00"
    assert card_after["available_limit"] == "800.00"


def test_pagamento_e_isolado_por_usuario(client, db_session_factory):
    headers_a = auth_client(client)
    card = setup_card(client, headers_a, db_session_factory)
    create_purchase(client, headers_a, card["id"])
    invoice_id = invoice_id_of(client, headers_a, card["id"], "2026-12-01")

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    response = client.post(
        f"/api/cards/{card['id']}/invoices/{invoice_id}/payments",
        json={"amount": "150.00", "paid_at": "2026-12-10"},
        headers=headers_b,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "invoice_not_found"
