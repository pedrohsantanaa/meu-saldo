"""Testes da listagem unificada de movimentações (T-083).

Cenários: compras no cartão aparecem junto das movimentações comuns na
tela de Movimentações, identificadas pelo cartão utilizado e pela fatura
em que consolidam, com os mesmos filtros de consulta — sem nunca virar
movimentação comum (`spec.md` §7.2).
"""

from .test_auth import auth_headers, login, register
from .test_card_purchases import category_id, create_purchase, setup_card
from .test_cards import auth_client


def create_transaction(client, headers, **overrides):
    payload = {
        "type": "expense",
        "description": "Mercado do bairro",
        "amount": "80.00",
        "transaction_date": "2026-11-12",
        "category_id": category_id(client, headers, "Alimentação"),
        "expense_type": "variable",
        "payment_method": "pix",
    }
    payload.update(overrides)
    response = client.post("/api/transactions", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def movements(client, headers, **params):
    response = client.get("/api/movements", params=params, headers=headers)
    assert response.status_code == 200
    return response.json()


def setup_movements(client, headers, db_session_factory):
    card = setup_card(client, headers, db_session_factory)
    transaction = create_transaction(client, headers)
    purchase = create_purchase(
        client,
        headers,
        card["id"],
        description="Mercado atacadista",
        total_amount="150.00",
        purchase_date="2026-11-10",
    )
    return card, transaction, purchase


def test_lista_unificada_ordenada_por_data(client, db_session_factory):
    headers = auth_client(client)
    card, transaction, purchase = setup_movements(client, headers, db_session_factory)

    items = movements(client, headers)

    assert [item["source"] for item in items] == ["transaction", "card_purchase"]

    movement = items[0]
    assert movement["id"] == transaction["id"]
    assert movement["transaction_date"] == "2026-11-12"
    assert movement["type"] == "expense"
    assert movement["payment_method"] == "pix"

    bought = items[1]
    assert bought["id"] == purchase["id"]
    assert bought["source"] == "card_purchase"
    assert bought["transaction_date"] == "2026-11-10"
    assert bought["amount"] == "150.00"
    assert bought["type"] == "expense"
    # Particularidades: cartão utilizado e fatura em que consolida.
    assert bought["credit_card_id"] == card["id"]
    assert bought["card_name"] == "Nubank"
    assert bought["invoice_reference_month"] == "2026-12"
    assert bought["expense_type"] == "variable"


def test_filtro_por_periodo_e_categoria(client, db_session_factory):
    headers = auth_client(client)
    _card, _transaction, purchase = setup_movements(client, headers, db_session_factory)

    items = movements(client, headers, date_from="2026-11-10", date_to="2026-11-10")
    assert [item["source"] for item in items] == ["card_purchase"]

    items = movements(
        client,
        headers,
        category_id=category_id(client, headers, "Transporte/combustível"),
    )
    assert items == []


def test_filtro_por_tipo(client, db_session_factory):
    headers = auth_client(client)
    setup_movements(client, headers, db_session_factory)
    create_transaction(
        client,
        headers,
        type="income",
        description="Salário",
        amount="5000.00",
        transaction_date="2026-11-05",
        category_id=category_id(client, headers, "Salário"),
        expense_type=None,
        payment_method=None,
    )

    # "expense" inclui despesas comuns e compras; receitas ficam de fora.
    items = movements(client, headers, type="expense")
    assert {item["source"] for item in items} == {"transaction", "card_purchase"}

    items = movements(client, headers, type="income")
    assert [item["description"] for item in items] == ["Salário"]

    items = movements(client, headers, type="card_purchase")
    assert [item["source"] for item in items] == ["card_purchase"]


def test_filtro_por_forma_de_pagamento(client, db_session_factory):
    headers = auth_client(client)
    setup_movements(client, headers, db_session_factory)

    items = movements(client, headers, payment_method="pix")
    assert [item["source"] for item in items] == ["transaction"]

    # "credito" filtra as compras no cartão (particularidade).
    items = movements(client, headers, payment_method="credito")
    assert [item["source"] for item in items] == ["card_purchase"]


def test_filtro_por_cartao(client, db_session_factory):
    headers = auth_client(client)
    card, _transaction, _purchase = setup_movements(client, headers, db_session_factory)
    other = setup_card(client, headers, db_session_factory, name="Cartão B")

    items = movements(client, headers, card_id=card["id"])
    assert [item["credit_card_id"] for item in items] == [card["id"]]

    # Compra em outro cartão não aparece; movimentações comuns também não.
    create_purchase(
        client,
        headers,
        other["id"],
        description="Outro cartão",
        purchase_date="2026-11-11",
    )
    items = movements(client, headers, card_id=other["id"])
    assert [item["description"] for item in items] == ["Outro cartão"]


def test_busca_por_descricao(client, db_session_factory):
    headers = auth_client(client)
    setup_movements(client, headers, db_session_factory)

    items = movements(client, headers, search="bairro")
    assert [item["description"] for item in items] == ["Mercado do bairro"]

    items = movements(client, headers, search="Mercado")
    assert {item["source"] for item in items} == {"transaction", "card_purchase"}


def test_valores_invalidos_de_filtro_sao_rejeitados(client, db_session_factory):
    headers = auth_client(client)

    assert (
        client.get(
            "/api/movements", params={"type": "investimento"}, headers=headers
        ).status_code
        == 422
    )
    assert (
        client.get(
            "/api/movements", params={"payment_method": "boleto"}, headers=headers
        ).status_code
        == 422
    )


def test_movements_e_isolado_por_usuario(client, db_session_factory):
    headers_a = auth_client(client)
    setup_movements(client, headers_a, db_session_factory)

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    assert movements(client, headers_b) == []
