"""Testes de cartões de crédito (T-044, T-045) — AC-047 a AC-051."""

from datetime import datetime

from app.models import CreditCard

from .test_auth import auth_headers, login, register


def auth_client(client):
    register(client)
    token = login(client).json()["access_token"]
    return auth_headers(token)


def card_payload(**overrides):
    payload = {
        "name": "Nubank",
        "issuer": "Nubank",
        "credit_limit": "5000.00",
        "closing_day": 28,
        "due_day": 10,
    }
    payload.update(overrides)
    return payload


def create_card(client, headers, **overrides):
    response = client.post(
        "/api/cards", json=card_payload(**overrides), headers=headers
    )
    assert response.status_code == 201
    return response.json()


def backdate_card(db_session_factory, card_id, created_at: datetime):
    """Fixa a data de cadastro do cartão para testes de ciclo determinísticos
    (a primeira fatura começa no cadastro, AC-105)."""
    db = db_session_factory()
    try:
        card = db.get(CreditCard, card_id)
        card.created_at = created_at
        db.commit()
    finally:
        db.close()


def test_cadastrar_cartao(client):
    headers = auth_client(client)

    response = client.post("/api/cards", json=card_payload(), headers=headers)

    # AC-047: o cartão é criado e aparece na lista.
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Nubank"
    assert body["issuer"] == "Nubank"
    assert body["credit_limit"] == "5000.00"
    assert body["closing_day"] == 28
    assert body["due_day"] == 10
    assert body["is_active"] is True

    listing = client.get("/api/cards", headers=headers).json()
    assert [item["id"] for item in listing] == [body["id"]]


def test_lista_cartoes_inclui_indicadores_de_limite(client):
    headers = auth_client(client)
    create_card(client, headers)

    listing = client.get("/api/cards", headers=headers).json()

    # T-050: sem compras, comprometido é zero e disponível = limite.
    assert listing[0]["committed_amount"] == "0.00"
    assert listing[0]["available_limit"] == "5000.00"


def test_validar_dados_do_cartao(client):
    headers = auth_client(client)

    # AC-048: nome ausente, limite negativo e dias inválidos são rejeitados.
    for payload in (
        card_payload(name=""),
        card_payload(credit_limit="-1.00"),
        card_payload(closing_day=0),
        card_payload(closing_day=32),
        card_payload(due_day=0),
        card_payload(due_day=32),
    ):
        response = client.post("/api/cards", json=payload, headers=headers)
        assert response.status_code == 422, payload
        assert response.json()["error"]["code"] == "validation_error"


def test_nao_armazena_dados_sensiveis_do_cartao(client):
    headers = auth_client(client)

    body = create_card(client, headers)

    # AC-051: nem número do cartão, CVV, senha ou credenciais.
    sensitive = {"number", "card_number", "cvv", "password", "pin"}
    assert not sensitive & set(body.keys())


def test_editar_cartao(client):
    headers = auth_client(client)
    card = create_card(client, headers)

    response = client.put(
        f"/api/cards/{card['id']}",
        json={
            "name": "Nubank Ultravioleta",
            "credit_limit": "8000.00",
            "closing_day": 25,
            "due_day": 8,
        },
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Nubank Ultravioleta"
    assert body["credit_limit"] == "8000.00"
    assert body["closing_day"] == 25
    assert body["due_day"] == 8


def test_inativar_cartao_mantem_historico(client):
    headers = auth_client(client)
    card = create_card(client, headers)

    response = client.patch(
        f"/api/cards/{card['id']}/status",
        json={"is_active": False},
        headers=headers,
    )

    # AC-050: inativar mantém o cartão consultável.
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    detail = client.get(f"/api/cards/{card['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["is_active"] is False

    # Reativação também é permitida.
    reactivated = client.patch(
        f"/api/cards/{card['id']}/status",
        json={"is_active": True},
        headers=headers,
    )
    assert reactivated.json()["is_active"] is True


def test_cartoes_sao_independentes_e_isolados_por_usuario(client):
    headers_a = auth_client(client)
    card_a = create_card(client, headers_a, name="Cartão A")
    create_card(client, headers_a, name="Cartão B")

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    # AC-049: operações afetam somente o cartão selecionado.
    listing_a = client.get("/api/cards", headers=headers_a).json()
    assert {item["name"] for item in listing_a} == {"Cartão A", "Cartão B"}

    # Isolamento: os cartões de um usuário não aparecem para o outro.
    listing_b = client.get("/api/cards", headers=headers_b).json()
    assert listing_b == []

    response = client.get(f"/api/cards/{card_a['id']}", headers=headers_b)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "card_not_found"

    response = client.put(
        f"/api/cards/{card_a['id']}",
        json={"name": "Invadido"},
        headers=headers_b,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "card_not_found"
