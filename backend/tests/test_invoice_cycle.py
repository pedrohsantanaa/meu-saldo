"""Testes do ciclo de fatura (T-048) — AC-101 a AC-105.

Funções puras, sem banco: os casos reproduzem os exemplos de
`spec.md` §7.4 (fechamento dia 28, vencimento dia 10).
"""

from datetime import date

from app.services.invoice_cycle import (
    closing_after,
    due_after,
    resolve_invoice_cycle,
)

CARD_START = date(2026, 1, 15)


def cycle_of(purchase_date, closing_day=28, due_day=10, card_start=CARD_START):
    return resolve_invoice_cycle(closing_day, due_day, purchase_date, card_start)


def test_compra_antes_do_fechamento_entra_no_ciclo_do_mes():
    # Exemplo 1 (spec §7.4): compra em 10/11 fecha em 28/11 e vence 10/12.
    cycle = cycle_of(date(2026, 11, 10))

    assert cycle.closing_date == date(2026, 11, 28)
    assert cycle.due_date == date(2026, 12, 10)


def test_fatura_e_identificada_pelo_mes_do_vencimento():
    # AC-101: a fatura do ciclo que fecha em 28/11 é a "fatura de dezembro".
    cycle = cycle_of(date(2026, 11, 10))

    assert cycle.reference_month == date(2026, 12, 1)


def test_compra_apos_o_fechamento_entra_no_ciclo_seguinte():
    # AC-102 (exemplo 1): compra em 29/11 fecha em 28/12 e vence em 10/01.
    cycle = cycle_of(date(2026, 11, 29))

    assert cycle.closing_date == date(2026, 12, 28)
    assert cycle.due_date == date(2027, 1, 10)
    assert cycle.reference_month == date(2027, 1, 1)


def test_compra_no_dia_do_fechamento_entra_no_ciclo_seguinte():
    # AC-103: o ciclo encerra no início do dia do fechamento.
    cycle = cycle_of(date(2026, 11, 28))

    assert cycle.closing_date == date(2026, 12, 28)
    assert cycle.due_date == date(2027, 1, 10)


def test_fechamento_inexistente_em_mes_curto_usa_ultimo_dia():
    # AC-104: fechamento dia 31 em fevereiro (28 dias em 2026).
    assert closing_after(31, date(2026, 2, 10)) == date(2026, 2, 28)


def test_compra_no_ultimo_dia_de_mes_curto_entra_no_ciclo_seguinte():
    # AC-103 + AC-104: 28/02 é o fechamento de fevereiro (dia 31 inexistente).
    cycle = cycle_of(date(2026, 2, 28), closing_day=31)

    assert cycle.closing_date == date(2026, 3, 31)


def test_vencimento_inexistente_em_mes_curto_usa_ultimo_dia():
    # AC-104: vencimento dia 31 após fechar em 28/02 cai em 31/03.
    assert due_after(31, date(2026, 2, 28)) == date(2026, 3, 31)


def test_primeira_fatura_vai_do_cadastro_ao_primeiro_fechamento():
    # AC-105: cartão criado em 20/11 fecha em 28/11.
    cycle = resolve_invoice_cycle(
        28, 10, purchase_date=date(2026, 11, 21), card_start=date(2026, 11, 20)
    )

    assert cycle.closing_date == date(2026, 11, 28)


def test_compra_antes_do_cadastro_entra_na_primeira_fatura():
    # Registro retroativo: a compra é alocada à primeira fatura (AC-105).
    cycle = resolve_invoice_cycle(
        28, 10, purchase_date=date(2026, 11, 10), card_start=date(2026, 11, 20)
    )

    assert cycle.closing_date == date(2026, 11, 28)


def test_cartao_criado_no_dia_do_fechamento_so_fecha_no_mes_seguinte():
    # AC-103 + AC-105: o fechamento do dia do cadastro já encerrou.
    cycle = resolve_invoice_cycle(
        28, 10, purchase_date=date(2026, 11, 28), card_start=date(2026, 11, 28)
    )

    assert cycle.closing_date == date(2026, 12, 28)


def test_vencimento_apos_o_fechamento_fica_no_mes_do_fechamento():
    # Cartão com fechamento dia 5 e vencimento dia 20.
    cycle = cycle_of(date(2026, 12, 1), closing_day=5, due_day=20)

    assert cycle.closing_date == date(2026, 12, 5)
    assert cycle.due_date == date(2026, 12, 20)
    assert cycle.reference_month == date(2026, 12, 1)


def test_vencimento_antes_do_fechamento_vai_para_o_mes_seguinte():
    # Cartão com fechamento dia 28 e vencimento dia 10 (caso comum).
    cycle = cycle_of(date(2026, 12, 15), closing_day=28, due_day=10)

    assert cycle.due_date == date(2027, 1, 10)
    assert cycle.reference_month == date(2027, 1, 1)


def test_ciclos_sao_continuos_ao_longo_dos_meses():
    # Compras em datas vizinhas caem em ciclos coerentes (virada de ano).
    novembro = cycle_of(date(2026, 11, 27))
    dezembro = cycle_of(date(2026, 11, 28))

    assert novembro.closing_date == date(2026, 11, 28)
    assert dezembro.closing_date == date(2026, 12, 28)
    assert dezembro.reference_month == date(2027, 1, 1)


# --- T-061: meses com 28, 29, 30 e 31 dias e virada de ano ---------------


def test_mes_com_28_dias_fechamento_31_vira_28_de_fevereiro():
    # Fevereiro/2026 tem 28 dias.
    cycle = cycle_of(date(2026, 2, 1), closing_day=31, due_day=10)

    assert cycle.closing_date == date(2026, 2, 28)
    assert cycle.due_date == date(2026, 3, 10)


def test_mes_com_29_dias_fechamento_30_vira_29_de_fevereiro():
    # Fevereiro/2028 (bissexto) tem 29 dias.
    cycle = cycle_of(date(2028, 2, 1), closing_day=30, due_day=10)

    assert cycle.closing_date == date(2028, 2, 29)
    assert cycle.due_date == date(2028, 3, 10)


def test_compra_no_dia_29_de_fevereiro_bissexto_vai_para_o_ciclo_seguinte():
    cycle = cycle_of(date(2028, 2, 29), closing_day=30, due_day=10)

    assert cycle.closing_date == date(2028, 3, 30)


def test_mes_com_30_dias_fechamento_31_vira_30_de_abril():
    cycle = cycle_of(date(2026, 4, 1), closing_day=31, due_day=10)

    assert cycle.closing_date == date(2026, 4, 30)


def test_compra_no_dia_30_de_abril_entra_no_ciclo_seguinte():
    cycle = cycle_of(date(2026, 4, 30), closing_day=31, due_day=10)

    assert cycle.closing_date == date(2026, 5, 31)


def test_mes_com_31_dias_usa_o_dia_configurado():
    cycle = cycle_of(date(2026, 1, 15), closing_day=31, due_day=10)

    assert cycle.closing_date == date(2026, 1, 31)
    assert cycle.due_date == date(2026, 2, 10)


def test_virada_de_ano_no_ciclo_da_fatura():
    # Compra em 29/12/2026 (fechamento 28): ciclo fecha em 28/01/2027.
    cycle = cycle_of(date(2026, 12, 29))

    assert cycle.closing_date == date(2027, 1, 28)
    assert cycle.due_date == date(2027, 2, 10)
    assert cycle.reference_month == date(2027, 2, 1)


def test_virada_de_ano_no_vencimento_dia_31():
    # Fechamento 28/12: primeira ocorrência do dia 31 posterior é 31/12.
    assert due_after(31, date(2026, 12, 28)) == date(2026, 12, 31)

    # Já com fechamento em 31/12, o vencimento cai em janeiro (mês curto
    # de fevereiro também é ajustado: dia 31 → 28/02).
    assert due_after(31, date(2026, 12, 31)) == date(2027, 1, 31)
    assert due_after(31, date(2027, 1, 31)) == date(2027, 2, 28)
