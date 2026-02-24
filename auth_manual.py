"""
Autenticação manual com a API v3 do Tiny.

Fluxo padrão:
- Gere a URL de autorização com generate_auth_url().
- Acesse a URL no navegador, faça login e autorize.
- Copie o parâmetro `code` da URL de retorno.
- Use exchange_code_for_tokens() para salvar tokens em tiny_tokens.json.
- Use get_valid_access_token() nas chamadas à API.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from typing import Any, Dict, Optional

import requests

from settings import TinyConfig, load_config


TOKENS_EXPIRES_KEY = "expira_em_timestamp"


def _load_tokens(token_file: str) -> Optional[Dict[str, Any]]:
    try:
        with open(token_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        return None


def _save_tokens(token_file: str, new_data: Dict[str, Any], previous: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = previous.copy() if previous else {}
    data.update(new_data)

    # calcula timestamp de expiração do access token, se a API informar expires_in
    if "expires_in" in new_data:
        data[TOKENS_EXPIRES_KEY] = time.time() + int(new_data["expires_in"])

    with open(token_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def generate_auth_url(config: TinyConfig, scope: str = "openid offline_access") -> str:
    """
    Gera a URL de autorização para o fluxo OAuth do Tiny.
    """
    from urllib.parse import urlencode

    params = {
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "scope": scope,
        "response_type": "code",
    }
    return f"{config.url_auth}?{urlencode(params)}"


def exchange_code_for_tokens(code: str, config: Optional[TinyConfig] = None) -> Dict[str, Any]:
    """
    Troca um CODE (da URL de retorno) por access_token e refresh_token.
    Salva o resultado em tiny_tokens.json.
    """
    if config is None:
        config = load_config()

    payload = {
        "grant_type": "authorization_code",
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "redirect_uri": config.redirect_uri,
        "code": code,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    resp = requests.post(config.url_token, data=payload, headers=headers, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Erro ao trocar CODE por tokens (status {resp.status_code}): {resp.text}"
        )

    tokens = resp.json()
    _save_tokens(config.token_file, tokens)
    return tokens


def refresh_access_token(config: Optional[TinyConfig] = None) -> Dict[str, Any]:
    """
    Renova o access_token usando o refresh_token salvo em tiny_tokens.json.
    """
    if config is None:
        config = load_config()

    current_tokens = _load_tokens(config.token_file)
    if not current_tokens or "refresh_token" not in current_tokens:
        raise RuntimeError("Nenhum refresh_token encontrado. Gere um novo CODE primeiro.")

    payload = {
        "grant_type": "refresh_token",
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "refresh_token": current_tokens["refresh_token"],
    }

    resp = requests.post(config.url_token, data=payload, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Erro ao renovar tokens (status {resp.status_code}): {resp.text}"
        )

    tokens = resp.json()
    merged = _save_tokens(config.token_file, tokens, previous=current_tokens)
    return merged


def get_valid_access_token(config: Optional[TinyConfig] = None) -> str:
    """
    Retorna um access_token válido.

    Regras:
    - Se não existir tiny_tokens.json: levanta erro explicando que é necessário
      primeiro gerar tokens com exchange_code_for_tokens().
    - Se o access_token estiver expirado mas ainda houver refresh_token: renova.
    - Caso não seja possível renovar, levanta erro para que o usuário gere um novo CODE.
    """
    if config is None:
        config = load_config()

    tokens = _load_tokens(config.token_file)
    if not tokens:
        raise RuntimeError(
            "Arquivo de tokens não encontrado.\n"
            "Use generate_auth_url() e exchange_code_for_tokens() para gerar tokens antes de chamar a API."
        )

    # verifica expiração (margem de 5 minutos)
    now = time.time()
    expires_at = tokens.get(TOKENS_EXPIRES_KEY, 0)

    if now < (expires_at - 300):
        return tokens.get("access_token")

    # tenta renovar com refresh_token
    if "refresh_token" in tokens:
        new_tokens = refresh_access_token(config)
        return new_tokens.get("access_token")

    raise RuntimeError(
        "Access token expirado e nenhum refresh_token disponível.\n"
        "Gere um novo CODE e chame exchange_code_for_tokens() novamente."
    )


def debug_dump_config(config: Optional[TinyConfig] = None) -> Dict[str, Any]:
    """
    Utilitário apenas para debug/manual: imprime configuração básica sem segredos.
    Não é usado pelo fluxo principal.
    """
    if config is None:
        config = load_config()

    data = asdict(config)
    # não expor segredos em logs
    data["client_id"] = "***"
    data["client_secret"] = "***"
    data["tiny_username"] = bool(config.tiny_username)
    data["tiny_password"] = bool(config.tiny_password)
    return data

