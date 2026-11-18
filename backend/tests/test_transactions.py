from .test_auth import auth_headers, login, register


def auth_client(client):
    register(client)
    token = login(client).json()["access_token"]
    return auth_headers(token)


def category_id(client, headers, name):
    categories = client.get("/api/categories", headers=headers).json()
    return next(item["id"] for item in categories if item["name"] == name)


def income_payload(client, headers, **overrides):
    payload = {
        "type": "income",
        "description": "Salário IF",
        "amount": "7175.09",
        "transaction_date": "2026-11-01",
        "category_id": category_id(client, headers, "Salário"),
    }
    payload.update(overrides)
    return payload


def expense_payload(client, headers, **overrides):
    payload = {
        "type": "expense",
        "description": "Supermercado",
        "amount": "385.26",
        "transaction_date": "2026-11-15",
        "category_id": category_id(client, headers, "Alimentação"),
        "expense_type": "variable",
        "payment_method": "pix",
    }
    payload.update(overrides)
    return payload


def test_criar_receita(client):
    headers = auth_client(client)

    response = client.post(
        "/api/transactions", json=income_payload(client, headers), headers=headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "income"
    assert body["amount"] == "7175.09"
    assert body["transaction_date"] == "2026-11-01"


def test_criar_despesa_completa(client):
    headers = auth_client(client)

    response = client.post(
        "/api/transactions", json=expense_payload(client, headers), headers=headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["expense_type"] == "variable"
    assert body["payment_method"] == "pix"


def test_criar_investimento(client):
    headers = auth_client(client)

    response = client.post(
        "/api/transactions",
        json={
            "type": "investment",
            "description": "Poupança",
            "amount": "500.00",
            "transaction_date": "2026-11-10",
            "category_id": category_id(client, headers, "Poupança"),
        },
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["type"] == "investment"


def test_valor_deve_ser_positivo(client):
    headers = auth_client(client)

    response = client.post(
        "/api/transactions",
        json=income_payload(client, headers, amount="0"),
        headers=headers,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_despesa_exige_classificacao_e_forma_de_pagamento(client):
    headers = auth_client(client)

    sem_classificacao = client.post(
        "/api/transactions",
        json=expense_payload(client, headers, expense_type=None),
        headers=headers,
    )
    sem_forma = client.post(
        "/api/transactions",
        json=expense_payload(client, headers, payment_method=None),
        headers=headers,
    )

    assert sem_classificacao.status_code == 400
    assert sem_classificacao.json()["error"]["code"] == "expense_type_required"
    assert sem_forma.status_code == 400
    assert sem_forma.json()["error"]["code"] == "payment_method_required"


def test_categoria_incompativel_e_rejeitada(client):
    headers = auth_client(client)

    response = client.post(
        "/api/transactions",
        json=income_payload(
            client, headers, category_id=category_id(client, headers, "Alimentação")
        ),
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "category_type_mismatch"


def test_categoria_inativa_e_rejeitada(client):
    headers = auth_client(client)
    salario = category_id(client, headers, "Salário")
    client.patch(
        f"/api/categories/{salario}/status", json={"is_active": False}, headers=headers
    )

    response = client.post(
        "/api/transactions", json=income_payload(client, headers), headers=headers
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "inactive_category"


def test_filtrar_movimentacoes(client):
    headers = auth_client(client)
    client.post(
        "/api/transactions", json=income_payload(client, headers), headers=headers
    )
    client.post(
        "/api/transactions", json=expense_payload(client, headers), headers=headers
    )
    client.post(
        "/api/transactions",
        json=expense_payload(
            client,
            headers,
            description="Barbeiro",
            amount="150.00",
            transaction_date="2026-11-03",
        ),
        headers=headers,
    )

    por_tipo = client.get(
        "/api/transactions", params={"type": "expense"}, headers=headers
    ).json()
    por_periodo = client.get(
        "/api/transactions",
        params={"date_from": "2026-11-05", "date_to": "2026-11-30"},
        headers=headers,
    ).json()
    por_busca = client.get(
        "/api/transactions", params={"search": "Barbeiro"}, headers=headers
    ).json()

    assert len(por_tipo) == 2
    assert {item["description"] for item in por_periodo} == {"Supermercado"}
    assert [item["description"] for item in por_busca] == ["Barbeiro"]


def test_editar_e_excluir_movimentacao(client):
    headers = auth_client(client)
    created = client.post(
        "/api/transactions", json=income_payload(client, headers), headers=headers
    ).json()

    updated = client.put(
        f"/api/transactions/{created['id']}",
        json={"amount": "8000.00", "description": "Salário reajustado"},
        headers=headers,
    )
    deleted = client.delete(f"/api/transactions/{created['id']}", headers=headers)
    after_delete = client.get(f"/api/transactions/{created['id']}", headers=headers)

    assert updated.status_code == 200
    assert updated.json()["amount"] == "8000.00"
    assert deleted.status_code == 204
    assert after_delete.status_code == 404


def test_isolamento_de_movimentacoes_entre_usuarios(client):
    """Acesso por alteração de IDs deve falhar entre usuários (T-025, AC-009)."""
    headers_a = auth_client(client)
    created = client.post(
        "/api/transactions", json=income_payload(client, headers_a), headers=headers_a
    ).json()

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    get_b = client.get(f"/api/transactions/{created['id']}", headers=headers_b)
    update_b = client.put(
        f"/api/transactions/{created['id']}", json={"amount": "1.00"}, headers=headers_b
    )
    delete_b = client.delete(f"/api/transactions/{created['id']}", headers=headers_b)
    list_b = client.get("/api/transactions", headers=headers_b).json()

    assert get_b.status_code == 404
    assert update_b.status_code == 404
    assert delete_b.status_code == 404
    assert list_b == []
