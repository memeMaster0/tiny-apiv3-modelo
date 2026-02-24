"""
Cliente HTTP genérico para a API v3 do Tiny.

Foco em operações GET paginadas com offset/limit.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

import requests

from settings import TinyConfig, load_config
from auth_manual import get_valid_access_token


def _build_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _extract_items(payload: Dict[str, Any], entity_key: Optional[str]) -> List[Dict[str, Any]]:
    """
    Extrai a lista de itens do payload JSON.
    - Se entity_key for informada, usa diretamente.
    - Caso contrário, tenta chaves comuns: 'itens', 'items', 'pedidos', 'produtos'.
    """
    if entity_key:
        data = payload.get(entity_key, [])
    else:
        for key in ("itens", "items", "pedidos", "produtos"):
            if key in payload:
                data = payload.get(key, [])
                break
        else:
            data = []

    return data or []


def get_paginated(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    entity_key: Optional[str] = None,
    config: Optional[TinyConfig] = None,
    limit_per_page: int = 100,
) -> List[Dict[str, Any]]:
    """
    Faz requisições GET paginadas à API do Tiny usando offset/limit.

    - endpoint: ex.: "pedidos", "produtos"
    - params: dicionário de parâmetros adicionais (datas, filtros etc.)
    - entity_key: nome da chave no JSON que contém a lista (opcional)
    - limit_per_page: quantidade de registros por página (padrão 100)
    """
    if config is None:
        config = load_config()

    base_url = f"{config.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    token = get_valid_access_token(config)
    headers = _build_headers(token)

    all_items: List[Dict[str, Any]] = []
    offset = 0
    max_pages = 1000  # proteção contra loop infinito

    for page in range(max_pages):
        query: Dict[str, Any] = {"offset": offset, "limit": limit_per_page}
        if params:
            query.update(params)

        resp = requests.get(base_url, headers=headers, params=query, timeout=60)

        # tratamento básico de erros
        if resp.status_code == 401:
            # tenta renovar o token automaticamente uma vez
            token = get_valid_access_token(config)
            headers = _build_headers(token)
            resp = requests.get(base_url, headers=headers, params=query, timeout=60)

        if resp.status_code == 429:
            # limite de requisições atingido: aguarda alguns segundos e tenta novamente
            time.sleep(5)
            resp = requests.get(base_url, headers=headers, params=query, timeout=60)

        if resp.status_code != 200:
            raise RuntimeError(
                f"Erro ao chamar {base_url} (status {resp.status_code}): {resp.text}"
            )

        data = resp.json()
        items = _extract_items(data, entity_key=entity_key)

        if not items:
            break

        all_items.extend(items)

        # se veio menos do que o limite, assumimos que acabou
        if len(items) < limit_per_page:
            break

        offset += limit_per_page

        # pequeno intervalo para respeitar rate-limits
        time.sleep(1.0)

    return all_items

