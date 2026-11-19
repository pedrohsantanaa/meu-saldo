"""Testes de compras no cartão (T-046, T-047) — AC-053 a AC-057."""

from datetime import datetime

from .test_auth import auth_headers, login, register
from .test_cards import auth_client, backdate_card, create_card

CARD_START = datetime(2026, 1, 15)


def category_id(client, headers, name):
    categories = client.get("/api/categories", headers=headers).json()
    return next(item["id"] for item in categories if item["name"] == name)


def purchase_payload(client, headers, **overrides):
    payload = {
        "description": "Mercado do bairro",
        "total_amount": "150.00",
        "purchase_date": "2026-11-10",
        "category_id": category_id(client, headers, "Alimentação"),
    }
    payload.update(overrides)
    return payload


def setup_card(client, headers, db_session_factory, **overrides):
    card = create_card(client, headers, **overrides)
    backdate_card(db_session_factory, card["id"], CARD_START)
    return card


def create_purchase(client, headers, card_id, **overrides):
    response = client.post(
        f"/api/cards/{card_id}/purchases",
        json=purchase_payload(client, headers, **overrides),
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_registrar_compra_valida(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    body = create_purchase(client, headers, card["id"])

    # AC-053: compra associada ao cartão e a uma fatura.
    assert body["credit_card_id"] == card["id"]
    assert body["invoice_id"] is not None
    assert body["total_amount"] == "150.00"
    assert body["installments_count"] == 1


def test_compra_antes_do_fechamento_entra_na_fatura_do_ciclo(
    client, db_session_factory
):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    create_purchase(client, headers, card["id"], purchase_date="2026-11-10")

    # AC-055/AC-101: fecha em 28/11 e vence em 10/12 — fatura de dezembro.
    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()
    assert len(invoices) == 1
    assert invoices[0]["reference_month"] == "2026-12-01"
    assert invoices[0]["closing_date"] == "2026-11-28"
    assert invoices[0]["due_date"] == "2026-12-10"
    assert invoices[0]["total"] == "150.00"


def test_compra_no_dia_do_fechamento_entra_no_ciclo_seguinte(
    client, db_session_factory
):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    create_purchase(client, headers, card["id"], purchase_date="2026-11-28")

    # AC-103: fecha em 28/12 e vence em 10/01 — fatura de janeiro.
    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()
    assert len(invoices) == 1
    assert invoices[0]["reference_month"] == "2027-01-01"
    assert invoices[0]["closing_date"] == "2026-12-28"
    assert invoices[0]["due_date"] == "2027-01-10"


def test_impedir_compra_em_cartao_inativo(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    client.patch(
        f"/api/cards/{card['id']}/status",
        json={"is_active": False},
        headers=headers,
    )

    response = client.post(
        f"/api/cards/{card['id']}/purchases",
        json=purchase_payload(client, headers),
        headers=headers,
    )

    # AC-054: cartão inativo não aceita novas compras.
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "inactive_card"


def test_compra_exige_categoria_de_despesa(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    response = client.post(
        f"/api/cards/{card['id']}/purchases",
        json=purchase_payload(
            client, headers, category_id=category_id(client, headers, "Poupança")
        ),
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "category_type_mismatch"


def test_compra_rejeita_categoria_inativa(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    category = category_id(client, headers, "Alimentação")
    client.patch(
        f"/api/categories/{category}/status", json={"is_active": False}, headers=headers
    )

    response = client.post(
        f"/api/cards/{card['id']}/purchases",
        json=purchase_payload(client, headers),
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "inactive_category"


def test_valor_da_compra_deve_ser_positivo(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    response = client.post(
        f"/api/cards/{card['id']}/purchases",
        json=purchase_payload(client, headers, total_amount="0"),
        headers=headers,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_editar_compra_atualiza_o_total_da_fatura(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    purchase = create_purchase(client, headers, card["id"])

    response = client.put(
        f"/api/cards/{card['id']}/purchases/{purchase['id']}",
        json={"total_amount": "200.00"},
        headers=headers,
    )

    # AC-057: total da fatura recalculado.
    assert response.status_code == 200
    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()
    assert invoices[0]["total"] == "200.00"


def test_editar_data_move_a_compra_de_fatura(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    purchase = create_purchase(client, headers, card["id"])

    # Sai do ciclo que fecha em 28/11 e entra no que fecha em 28/12.
    client.put(
        f"/api/cards/{card['id']}/purchases/{purchase['id']}",
        json={"purchase_date": "2026-11-29"},
        headers=headers,
    )

    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()
    assert len(invoices) == 1
    assert invoices[0]["reference_month"] == "2027-01-01"
    assert invoices[0]["total"] == "150.00"


def test_excluir_compra_atualiza_a_fatura(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    purchase = create_purchase(client, headers, card["id"])

    response = client.delete(
        f"/api/cards/{card['id']}/purchases/{purchase['id']}", headers=headers
    )

    # AC-057: sem compras nem pagamentos, a fatura vazia é removida.
    assert response.status_code == 204
    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers).json()
    assert invoices == []


def test_compras_sao_isoladas_por_usuario(client, db_session_factory):
    headers_a = auth_client(client)
    card = setup_card(client, headers_a, db_session_factory)
    purchase = create_purchase(client, headers_a, card["id"])

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    listing = client.get(f"/api/cards/{card['id']}/purchases", headers=headers_b)
    # O cartão pertence a outro usuário.
    assert listing.status_code == 404
    assert listing.json()["error"]["code"] == "card_not_found"

    response = client.put(
        f"/api/cards/{card['id']}/purchases/{purchase['id']}",
        json={"total_amount": "999.00"},
        headers=headers_b,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "purchase_not_found"
