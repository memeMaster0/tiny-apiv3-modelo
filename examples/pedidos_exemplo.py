from __future__ import annotations

from datetime import datetime, timedelta

from settings import load_config
from tiny_client import get_paginated
from reporting import to_excel


def _first_day_and_last_day_previous_month(today: datetime) -> tuple[datetime, datetime]:
    first_day_this_month = today.replace(day=1)
    last_day_previous_month = first_day_this_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    return first_day_previous_month, last_day_previous_month


def extract_pedidos_months_example() -> None:
    """
    Exemplo simples:
    - Extrai pedidos do mês atual.
    - Extrai pedidos do mês anterior.
    - Salva um arquivo Excel por mês na pasta configurada.
    """
    config = load_config()
    today = datetime.now()

    periods = []

    # mês atual
    first_day_current = today.replace(day=1)
    periods.append(
        (
            "mes_atual",
            first_day_current.strftime("%Y-%m-%d"),
            today.strftime("%Y-%m-%d"),
        )
    )

    # mês anterior
    first_prev, last_prev = _first_day_and_last_day_previous_month(today)
    periods.append(
        (
            "mes_anterior",
            first_prev.strftime("%Y-%m-%d"),
            last_prev.strftime("%Y-%m-%d"),
        )
    )

    for label, start_date, end_date in periods:
        params = {
            "dataInicial": start_date,
            "dataFinal": end_date,
        }
        pedidos = get_paginated("pedidos", params=params, entity_key="pedidos", config=config)

        month_label = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m.%Y")
        filename = f"pedidos_{label}_{month_label}.xlsx"

        output_path = to_excel(pedidos, config.reports_pedidos_dir, filename)
        print(f"Relatório de pedidos ({label}) salvo em: {output_path}")

