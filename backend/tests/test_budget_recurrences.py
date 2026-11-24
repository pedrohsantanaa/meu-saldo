"""Testes da recorrência de orçamento: parcelas e repetição (T-075).

Cenários: AC-116 a AC-120 — valor total parcelado com soma exata,
valor repetido por N meses, criação atômica, exclusão de série e
edição mês a mês sem propagação.
"""

from decimal import Decimal

from app.services.budget_recurrences import split_amounts

from .test_auth import auth_headers, login, register
from .test_card_purchases import category_id, setup_card
from .test_transactions import auth_client

SERIES_MONTHS = ["2026-10", "2026-11", "2026-12"]


def create_series(client, headers, card_id, **overrides):
    payload = {
        "card_id": card_id,
        "category_id": category_id(client, headers, "Alimentação"),
        "month": "2026-10",
        "recurrence": {"mode": "installments", "amount": "600.00", "count": 3},
    }
    payload.update(overrides)
    response = client.post("/api/budgets/recurrences", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def create_general_series(client, headers, **overrides):
    payload = {
        "category_id": category_id(client, headers, "Alimentação"),
        "month": "2026-10",
        "recurrence": {"mode": "installments", "amount": "600.00", "count": 3},
    }
    payload.update(overrides)
    response = client.post(
        "/api/budgets/general/recurrences", json=payload, headers=headers
    )
    assert response.status_code == 201
    return response.json()


def card_summary(client, headers, card_id, month):
    return client.get(
        "/api/budgets", params={"month": month, "card_id": card_id}, headers=headers
    ).json()


def general_summary(client, headers, month):
    return client.get(
        "/api/budgets/general", params={"month": month}, headers=headers
    ).json()


def row_of(summary, name="Alimentação"):
    return next(item for item in summary["rows"] if item["category_name"] == name)


def test_dividir_valor_total_em_parcelas_com_soma_exata():
    # AC-116: soma exata, com os centavos na última parcela (§7.3).
    assert split_amounts(Decimal("100.00"), 3) == [
        Decimal("33.33"),
        Decimal("33.33"),
        Decimal("33.34"),
    ]
    assert split_amounts(Decimal("600.00"), 3) == [
        Decimal("200.00"),
        Decimal("200.00"),
        Decimal("200.00"),
    ]
    assert sum(split_amounts(Decimal("10.00"), 3)) == Decimal("10.00")
    assert split_amounts(Decimal("0.01"), 2) == [
        Decimal("0.00"),
        Decimal("0.01"),
    ]


def test_criar_orcamento_parcelado(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    body = create_series(
        client,
        headers,
        card["id"],
        recurrence={"mode": "installments", "amount": "600.00", "count": 3},
    )

    # AC-116: 3 parcelas de R$ 200 nos meses seguidos a partir do inicial.
    assert body["recurrence"]["mode"] == "installments"
    assert body["recurrence"]["amount"] == "600.00"
    assert body["recurrence"]["count"] == 3
    assert body["months"] == SERIES_MONTHS
    assert [row["budget_amount"] for row in body["rows"]] == [
        "200.00",
        "200.00",
        "200.00",
    ]


def test_parcelas_somam_o_valor_total(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    body = create_series(
        client,
        headers,
        card["id"],
        recurrence={"mode": "installments", "amount": "100.00", "count": 3},
    )

    assert [row["budget_amount"] for row in body["rows"]] == [
        "33.33",
        "33.33",
        "33.34",
    ]
    total = sum(Decimal(row["budget_amount"]) for row in body["rows"])
    assert total == Decimal("100.00")


def test_criar_orcamento_repetido(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    body = create_series(
        client,
        headers,
        card["id"],
        recurrence={"mode": "monthly", "amount": "300.00", "count": 3},
    )

    # AC-117: o valor mensal se repete por N meses.
    assert body["recurrence"]["mode"] == "monthly"
    assert [row["budget_amount"] for row in body["rows"]] == [
        "300.00",
        "300.00",
        "300.00",
    ]


def test_meses_da_serie_atravessam_o_ano(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)

    body = create_series(
        client,
        headers,
        card["id"],
        month="2026-11",
        recurrence={"mode": "monthly", "amount": "100.00", "count": 3},
    )

    assert body["months"] == ["2026-11", "2026-12", "2027-01"]


def test_conflito_com_mes_ja_orçado_e_criacao_atomica(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    client.post(
        "/api/budgets",
        json={
            "card_id": card["id"],
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-11",
            "budget_amount": "50.00",
        },
        headers=headers,
    )

    response = client.post(
        "/api/budgets/recurrences",
        json={
            "card_id": card["id"],
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-10",
            "recurrence": {"mode": "monthly", "amount": "100.00", "count": 3},
        },
        headers=headers,
    )

    # AC-118: nada é criado e os meses em conflito são informados.
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "budget_already_exists"
    assert error["details"]["months"] == ["2026-11"]
    assert card_summary(client, headers, card["id"], "2026-10")["rows"] == []
    assert card_summary(client, headers, card["id"], "2026-12")["rows"] == []


def test_serie_geral_sem_cartao(client):
    headers = auth_client(client)

    body = create_general_series(
        client,
        headers,
        recurrence={"mode": "monthly", "amount": "250.00", "count": 2},
    )

    assert body["months"] == ["2026-10", "2026-11"]
    assert [row["budget_amount"] for row in body["rows"]] == ["250.00", "250.00"]
    row = row_of(general_summary(client, headers, "2026-11"))
    assert row["recurrence"]["mode"] == "monthly"
    assert row["recurrence"]["position"] == 2
    assert row["recurrence"]["total"] == 2


def test_badge_da_serie_nas_linhas(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    body = create_series(client, headers, card["id"])

    remaining = {"2026-10": "600.00", "2026-11": "400.00", "2026-12": "200.00"}
    for position, month in enumerate(SERIES_MONTHS, start=1):
        row = row_of(card_summary(client, headers, card["id"], month))
        assert row["recurrence"] == {
            "id": body["recurrence"]["id"],
            "mode": "installments",
            "position": position,
            "total": 3,
            "amount": "600.00",
            "remaining_total": remaining[month],
        }


def test_editar_mes_da_serie_afeta_somente_aquele_mes(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    body = create_series(client, headers, card["id"])

    # AC-120: editar a segunda parcela não altera as demais.
    response = client.put(
        f"/api/budgets/{body['rows'][1]['id']}",
        json={"budget_amount": "250.00"},
        headers=headers,
    )
    assert response.status_code == 200

    amounts = [
        row_of(card_summary(client, headers, card["id"], month))["budget_amount"]
        for month in SERIES_MONTHS
    ]
    assert amounts == ["200.00", "250.00", "200.00"]


def test_excluir_linha_mantem_o_restante_da_serie(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    body = create_series(client, headers, card["id"])

    response = client.delete(f"/api/budgets/{body['rows'][0]['id']}", headers=headers)
    assert response.status_code == 204

    assert card_summary(client, headers, card["id"], "2026-10")["rows"] == []
    for month in ("2026-11", "2026-12"):
        row = row_of(card_summary(client, headers, card["id"], month))
        assert row["id"] is not None


def test_excluir_serie_remove_todos_os_meses(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    body = create_series(client, headers, card["id"])

    response = client.delete(
        f"/api/budgets/recurrences/{body['recurrence']['id']}", headers=headers
    )

    # AC-119: todas as linhas geradas são removidas.
    assert response.status_code == 204
    for month in SERIES_MONTHS:
        assert card_summary(client, headers, card["id"], month)["rows"] == []


def test_validacoes_de_recorrencia(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    category = category_id(client, headers, "Alimentação")

    for recurrence in (
        {"mode": "installments", "amount": "100.00", "count": 1},
        {"mode": "installments", "amount": "100.00", "count": 61},
        {"mode": "monthly", "amount": "0.00", "count": 3},
        {"mode": "parcelado", "amount": "100.00", "count": 3},
    ):
        response = client.post(
            "/api/budgets/recurrences",
            json={
                "card_id": card["id"],
                "category_id": category,
                "month": "2026-10",
                "recurrence": recurrence,
            },
            headers=headers,
        )
        assert response.status_code == 422, recurrence

    response = client.post(
        "/api/budgets/recurrences",
        json={
            "card_id": card["id"],
            "category_id": category_id(client, headers, "Salário"),
            "month": "2026-10",
            "recurrence": {"mode": "monthly", "amount": "100.00", "count": 3},
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "category_type_mismatch"


def test_series_sao_isoladas_por_usuario(client, db_session_factory):
    headers_a = auth_client(client)
    card = setup_card(client, headers_a, db_session_factory)
    body = create_series(client, headers_a, card["id"])

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )

    response = client.delete(
        f"/api/budgets/recurrences/{body['recurrence']['id']}", headers=headers_b
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "recurrence_not_found"


def test_exclusao_de_serie_respeita_o_escopo(client, db_session_factory):
    headers = auth_client(client)
    body = create_general_series(client, headers)

    # Série geral não pode ser excluída pelo endpoint de cartão.
    response = client.delete(
        f"/api/budgets/recurrences/{body['recurrence']['id']}", headers=headers
    )
    assert response.status_code == 404

    response = client.delete(
        f"/api/budgets/general/recurrences/{body['recurrence']['id']}", headers=headers
    )
    assert response.status_code == 204


# --- Recorrência ativada/reconfigurada na edição -------------------------


def create_single_budget(client, headers, card_id, month="2026-10", amount="100.00"):
    response = client.post(
        "/api/budgets",
        json={
            "card_id": card_id,
            "category_id": category_id(client, headers, "Alimentação"),
            "month": month,
            "budget_amount": amount,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def attach_series(client, headers, budget_id, **recurrence):
    payload = {"mode": "monthly", "amount": "200.00", "count": 3}
    payload.update(recurrence)
    return client.put(
        f"/api/budgets/{budget_id}/recurrence", json=payload, headers=headers
    )


def test_ativar_recorrencia_na_edicao_converte_em_serie(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    budget = create_single_budget(client, headers, card["id"])

    response = attach_series(
        client,
        headers,
        budget["id"],
        mode="installments",
        amount="100.00",
        count=3,
    )

    # A série começa no mês editado (1º período) e parcela o valor total.
    assert response.status_code == 200
    body = response.json()
    assert body["months"] == SERIES_MONTHS
    assert [row["budget_amount"] for row in body["rows"]] == [
        "33.33",
        "33.33",
        "33.34",
    ]
    # A linha do mês editado é reaproveitada — nunca duplicada.
    assert body["rows"][0]["id"] == budget["id"]
    row = row_of(card_summary(client, headers, card["id"], "2026-10"))
    assert row["recurrence"]["position"] == 1
    assert row["recurrence"]["total"] == 3


def test_reconfigurar_serie_preserva_os_meses_anteriores(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    body = create_series(
        client,
        headers,
        card["id"],
        recurrence={"mode": "monthly", "amount": "200.00", "count": 3},
    )

    # Edita a segunda linha (2026-11): nova configuração a partir dela.
    response = attach_series(
        client,
        headers,
        body["rows"][1]["id"],
        mode="monthly",
        amount="300.00",
        count=2,
    )

    assert response.status_code == 200
    amounts = [
        row_of(card_summary(client, headers, card["id"], month))["budget_amount"]
        for month in SERIES_MONTHS
    ]
    # Meses anteriores intactos; a partir do mês editado, o novo valor.
    assert amounts == ["200.00", "300.00", "300.00"]
    # Badge coerente: meses preservados + novo horizonte.
    row = row_of(card_summary(client, headers, card["id"], "2026-11"))
    assert row["recurrence"]["position"] == 2
    assert row["recurrence"]["total"] == 3


def test_reduzir_o_horizonte_remove_os_meses_excedentes(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    body = create_series(
        client,
        headers,
        card["id"],
        recurrence={"mode": "monthly", "amount": "200.00", "count": 3},
    )

    response = attach_series(
        client,
        headers,
        body["rows"][0]["id"],
        mode="monthly",
        amount="100.00",
        count=2,
    )

    assert response.status_code == 200
    amounts = [
        row_of(card_summary(client, headers, card["id"], month))["budget_amount"]
        for month in ("2026-10", "2026-11")
    ]
    assert amounts == ["100.00", "100.00"]
    # Dezembro fica fora do novo horizonte e deixa de existir.
    assert card_summary(client, headers, card["id"], "2026-12")["rows"] == []


def test_conflito_bloqueia_a_geracao_na_edicao(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    budget = create_single_budget(client, headers, card["id"])
    create_single_budget(client, headers, card["id"], month="2026-12", amount="50.00")

    response = attach_series(client, headers, budget["id"])

    # AC-118 (mesmo comportamento da criação): nada muda e os meses em
    # conflito são informados.
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "budget_already_exists"
    assert error["details"]["months"] == ["2026-12"]
    row = row_of(card_summary(client, headers, card["id"], "2026-10"))
    assert row["budget_amount"] == "100.00"
    assert row["recurrence"] is None
    assert card_summary(client, headers, card["id"], "2026-11")["rows"] == []


def test_recorrencia_geral_ativada_na_edicao(client):
    headers = auth_client(client)
    response = client.post(
        "/api/budgets/general",
        json={
            "category_id": category_id(client, headers, "Alimentação"),
            "month": "2026-10",
            "budget_amount": "100.00",
        },
        headers=headers,
    )
    budget = response.json()

    response = client.put(
        f"/api/budgets/general/{budget['id']}/recurrence",
        json={"mode": "monthly", "amount": "250.00", "count": 2},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["months"] == ["2026-10", "2026-11"]
    assert [row["budget_amount"] for row in body["rows"]] == ["250.00", "250.00"]


def test_edicao_de_recorrencia_e_isolada_por_usuario(client, db_session_factory):
    headers_a = auth_client(client)
    card = setup_card(client, headers_a, db_session_factory)
    budget = create_single_budget(client, headers_a, card["id"])

    register(
        client, name="Bia Souza", email="bia@example.com", password="outra-senha-1"
    )
    headers_b = auth_headers(
        login(client, email="bia@example.com", password="outra-senha-1").json()[
            "access_token"
        ]
    )
    response = attach_series(client, headers_b, budget["id"])
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "budget_not_found"


def test_validacoes_de_recorrencia_na_edicao(client, db_session_factory):
    headers = auth_client(client)
    card = setup_card(client, headers, db_session_factory)
    budget = create_single_budget(client, headers, card["id"])

    for recurrence in (
        {"mode": "installments", "amount": "100.00", "count": 1},
        {"mode": "monthly", "amount": "100.00", "count": 61},
        {"mode": "monthly", "amount": "0.00", "count": 3},
    ):
        response = attach_series(client, headers, budget["id"], **recurrence)
        assert response.status_code == 422, recurrence
