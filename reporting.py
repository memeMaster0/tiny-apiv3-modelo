"""
Funções auxiliares para transformar dados da API em relatórios Excel.
"""

from __future__ import annotations

import os
from typing import Any, Iterable, List

import pandas as pd


def ensure_dir(path: str) -> None:
    """
    Garante que o diretório exista.
    """
    os.makedirs(path, exist_ok=True)


def to_dataframe(data: Iterable[dict]) -> pd.DataFrame:
    """
    Converte uma lista de dicionários em DataFrame, usando json_normalize.
    """
    data_list: List[dict] = list(data)
    if not data_list:
        return pd.DataFrame()

    return pd.json_normalize(data_list)


def to_excel(data: Iterable[dict], folder: str, filename: str) -> str:
    """
    Salva os dados em um arquivo Excel (.xlsx) e retorna o caminho final.
    """
    df = to_dataframe(data)
    ensure_dir(folder)

    output_path = os.path.join(folder, filename)
    if df.empty:
        # ainda assim cria um arquivo com cabeçalhos vazios, para indicar que não houve dados
        df.to_excel(output_path, index=False)
        return output_path

    df.to_excel(output_path, index=False)
    return output_path

