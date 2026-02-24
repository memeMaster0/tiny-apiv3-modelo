import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class TinyConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    api_base_url: str
    url_auth: str
    url_token: str
    token_file: str
    reports_pedidos_dir: str
    reports_produtos_dir: str
    tiny_username: str | None = None
    tiny_password: str | None = None


def load_config() -> TinyConfig:
    """
    Carrega variáveis de ambiente do .env e retorna o objeto de configuração.

    Este é o único lugar onde lemos o .env. Outros módulos recebem um TinyConfig.
    """
    # Carrega .env a partir da raiz do template
    base_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(base_dir, ".env"))

    client_id = os.getenv("TINY_CLIENT_ID")
    client_secret = os.getenv("TINY_CLIENT_SECRET")
    redirect_uri = os.getenv("TINY_REDIRECT_URI", "https://example.com/")

    if not client_id or not client_secret:
        raise RuntimeError(
            "TINY_CLIENT_ID e TINY_CLIENT_SECRET não encontrados.\n"
            "Crie um arquivo .env baseado em .env.example na pasta do projeto."
        )

    return TinyConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        api_base_url="https://api.tiny.com.br/public-api/v3",
        url_auth="https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/auth",
        url_token="https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token",
        token_file=os.path.join(base_dir, "tiny_tokens.json"),
        reports_pedidos_dir=os.getenv("REPORTS_PEDIDOS_DIR", os.path.join(base_dir, "relatorios", "pedidos")),
        reports_produtos_dir=os.getenv("REPORTS_PRODUTOS_DIR", os.path.join(base_dir, "relatorios", "produtos")),
        tiny_username=os.getenv("TINY_USERNAME") or None,
        tiny_password=os.getenv("TINY_PASSWORD") or None,
    )

