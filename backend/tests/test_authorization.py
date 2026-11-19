"""Testes de autorização e isolamento de dados (T-062).

Cenários: usuário não acessa cartão, movimentação, orçamento ou fatura de
outro usuário; rotas privadas exigem token (`spec.md` §9, AC-087). O
isolamento é aplicado no back-end por `get_current_user`
(`app/api/deps.py`) e pelas consultas filtradas por usuário.
"""

import pytest

from .test_auth import auth_headers, login, register
from .test_budgets import create_budget
from .test_card_purchases import category_id, create_purchase, setup_card
from .test_cards import auth_client


@pytest.fixture
def scenario(client, db_session_factory):
    """Usuário A com cartão, compra, fatura, orçamento e movimentação."""
    headers_a = auth_client(client)
    card = setup_card(client, headers_a, db_session_factory)
    purchase = create_purchase(client, headers_a, card["id"])
    invoices = client.get(f"/api/cards/{card['id']}/invoices", headers=headers_a).json()
    budget = create_budget(client, headers_a, card["id"])
    movement = client.post(
        "/api/transactions",
        json={
            "type": "income",
            "description": "Salário",
            "amount": "1000.00",
            "transaction_date": "2026-11-01",
            "category_id": category_id(client, headers_a, "Salário"),
        },
        headers=headers_a,
    ).json()

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )
    return {
        "headers_a": headers_a,
        "headers_b": headers_b,
        "card": card,
        "purchase": purchase,
        "invoice": invoices[0],
        "budget": budget,
        "movement": movement,
    }


def call(client, method, path, **kwargs):
    if method in {"post", "put", "patch"} and "json" not in kwargs:
        kwargs["json"] = {}
    return getattr(client, method)(path, **kwargs)


def test_nao_acessa_cartao_de_outro_usuario(client, scenario):
    card_id = scenario["card"]["id"]

    response = call(
        client, "get", f"/api/cards/{card_id}", headers=scenario["headers_b"]
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "card_not_found"

    response = call(
        client,
        "put",
        f"/api/cards/{card_id}",
        json={"name": "Invadido"},
        headers=scenario["headers_b"],
    )
    assert response.status_code == 404

    response = call(
        client,
        "patch",
        f"/api/cards/{card_id}/status",
        json={"is_active": False},
        headers=scenario["headers_b"],
    )
    assert response.status_code == 404


def test_nao_acessa_movimentacao_de_outro_usuario(client, scenario):
    movement_id = scenario["movement"]["id"]

    response = client.get(
        f"/api/transactions/{movement_id}", headers=scenario["headers_b"]
    )
    assert response.status_code == 404

    response = client.put(
        f"/api/transactions/{movement_id}",
        json={"amount": "999.00"},
        headers=scenario["headers_b"],
    )
    assert response.status_code == 404

    response = client.delete(
        f"/api/transactions/{movement_id}", headers=scenario["headers_b"]
    )
    assert response.status_code == 404


def test_nao_altera_orcamento_de_outro_usuario(client, scenario):
    budget_id = scenario["budget"]["id"]

    response = client.put(
        f"/api/budgets/{budget_id}",
        json={"budget_amount": "999.00"},
        headers=scenario["headers_b"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "budget_not_found"

    response = client.delete(f"/api/budgets/{budget_id}", headers=scenario["headers_b"])
    assert response.status_code == 404


def test_nao_consulta_fatura_de_outro_usuario(client, scenario):
    card_id = scenario["card"]["id"]
    invoice_id = scenario["invoice"]["id"]

    response = client.get(
        f"/api/cards/{card_id}/invoices", headers=scenario["headers_b"]
    )
    assert response.status_code == 404

    response = client.get(
        f"/api/cards/{card_id}/invoices/{invoice_id}", headers=scenario["headers_b"]
    )
    assert response.status_code == 404

    response = client.post(
        f"/api/cards/{card_id}/invoices/{invoice_id}/payments",
        json={"amount": "10.00", "paid_at": "2026-12-10"},
        headers=scenario["headers_b"],
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "invoice_not_found"


def test_nao_acessa_compra_de_outro_usuario(client, scenario):
    card_id = scenario["card"]["id"]
    purchase_id = scenario["purchase"]["id"]

    response = client.get(
        f"/api/cards/{card_id}/purchases/{purchase_id}", headers=scenario["headers_b"]
    )
    assert response.status_code == 404

    response = client.delete(
        f"/api/cards/{card_id}/purchases/{purchase_id}", headers=scenario["headers_b"]
    )
    assert response.status_code == 404


def test_nao_altera_categoria_de_outro_usuario(client, scenario):
    category = category_id(client, scenario["headers_a"], "Alimentação")

    response = client.put(
        f"/api/categories/{category}",
        json={"name": "Invadida"},
        headers=scenario["headers_b"],
    )
    assert response.status_code == 404

    response = client.patch(
        f"/api/categories/{category}/status",
        json={"is_active": False},
        headers=scenario["headers_b"],
    )
    assert response.status_code == 404


PRIVATE_ENDPOINTS = [
    ("get", "/api/auth/me"),
    ("get", "/api/categories"),
    ("post", "/api/categories"),
    ("get", "/api/transactions"),
    ("post", "/api/transactions"),
    ("get", "/api/cards"),
    ("post", "/api/cards"),
    ("get", "/api/budgets?month=2026-12&card_id=1"),
    ("post", "/api/budgets"),
    ("get", "/api/dashboard/monthly?month=2026-12"),
    ("get", "/api/dashboard/annual?year=2026"),
]


@pytest.mark.parametrize("method,path", PRIVATE_ENDPOINTS)
def test_rotas_privadas_exigem_autenticacao(client, method, path):
    # AC-087: nenhuma rota privada responde sem token.
    response = call(client, method, path)

    assert response.status_code == 401
    assert response.json()["error"]["code"] in {"unauthenticated", "invalid_token"}


def test_token_invalido_e_rejeitado(client):
    response = client.get("/api/auth/me", headers=auth_headers("token-fake"))

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"
