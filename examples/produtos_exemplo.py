from __future__ import annotations

from settings import load_config
from tiny_client import get_paginated
from reporting import to_excel


def extract_produtos_example() -> None:
    """
    Exemplo simples:
    - Extrai todos os produtos (estoque) disponíveis na API.
    - Salva um arquivo Excel único na pasta configurada.
    """
    config = load_config()

    produtos = get_paginated("produtos", entity_key="produtos", config=config)

    filename = "produtos_estoque_completo.xlsx"
    output_path = to_excel(produtos, config.reports_produtos_dir, filename)
    print(f"Relatório de produtos salvo em: {output_path}")

