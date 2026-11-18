from .test_auth import auth_headers, login, register


def auth_client(client):
    register(client)
    token = login(client).json()["access_token"]
    return auth_headers(token)


def create_category(
    client, headers, name="Viagem", group_type="expense", expense_type="variable"
):
    return client.post(
        "/api/categories",
        json={"name": name, "group_type": group_type, "expense_type": expense_type},
        headers=headers,
    )


def test_inscricao_cria_as_categorias_padrao(client):
    headers = auth_client(client)

    response = client.get("/api/categories", headers=headers)

    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 27
    assert {item["group_type"] for item in categories} == {
        "income",
        "expense",
        "investment",
    }
    assert all(item["is_default"] for item in categories)


def test_criar_categoria(client):
    headers = auth_client(client)

    response = create_category(client, headers)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Viagem"
    assert body["is_active"] is True


def test_nome_duplicado_no_mesmo_grupo_e_rejeitado(client):
    headers = auth_client(client)
    create_category(client, headers)

    response = create_category(client, headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "category_already_exists"


def test_mesmo_nome_em_grupos_diferentes_e_permitido(client):
    headers = auth_client(client)

    first = create_category(
        client, headers, name="Viagem", group_type="expense", expense_type="variable"
    )
    second = create_category(
        client, headers, name="Viagem", group_type="income", expense_type=None
    )

    assert first.status_code == second.status_code == 201


def test_despesa_exige_classificacao_fixa_ou_variavel(client):
    headers = auth_client(client)

    response = create_category(client, headers, expense_type=None)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "expense_type_required"


def test_receita_nao_aceita_classificacao_de_despesa(client):
    headers = auth_client(client)

    response = create_category(
        client, headers, group_type="income", expense_type="fixed"
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "expense_type_not_allowed"


def test_ativar_e_desativar_categoria(client):
    headers = auth_client(client)
    category_id = create_category(client, headers).json()["id"]

    disabled = client.patch(
        f"/api/categories/{category_id}/status",
        json={"is_active": False},
        headers=headers,
    )
    enabled = client.patch(
        f"/api/categories/{category_id}/status",
        json={"is_active": True},
        headers=headers,
    )

    assert disabled.json()["is_active"] is False
    assert enabled.json()["is_active"] is True


def test_editar_categoria(client):
    headers = auth_client(client)
    category_id = create_category(client, headers).json()["id"]

    response = client.put(
        f"/api/categories/{category_id}",
        json={"name": "Férias"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Férias"


def test_isolamento_de_categorias_entre_usuarios(client):
    headers_a = auth_client(client)
    category_id = create_category(client, headers_a, name="Viagem").json()["id"]

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    categories_b = client.get("/api/categories", headers=headers_b).json()
    assert all(item["name"] != "Viagem" for item in categories_b)

    update = client.put(
        f"/api/categories/{category_id}",
        json={"name": "Hackeada"},
        headers=headers_b,
    )
    status_update = client.patch(
        f"/api/categories/{category_id}/status",
        json={"is_active": False},
        headers=headers_b,
    )

    assert update.status_code == 404
    assert status_update.status_code == 404
