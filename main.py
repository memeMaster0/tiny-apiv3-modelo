"""
Ponto de entrada simples para o template modelo-apiv3-tiny.

Fluxo padrão ao rodar:
    python main.py

- Lê configurações do .env.
- Garante que você já gerou tokens (auth_manual.py).
- Executa exemplos de extração de pedidos e produtos.

Adapte este arquivo conforme a sua necessidade ou crie novos scripts
em `examples/` reaproveitando tiny_client.py e reporting.py.
"""

from __future__ import annotations

from auth_manual import generate_auth_url
from settings import load_config
from examples.pedidos_exemplo import extract_pedidos_months_example
from examples.produtos_exemplo import extract_produtos_example


def print_auth_instructions() -> None:
    """
    Exibe instruções básicas de autenticação manual.
    """
    config = load_config()
    url = generate_auth_url(config)

    print("=" * 72)
    print("AUTENTICAÇÃO MANUAL – PRIMEIRO USO")
    print("-" * 72)
    print("1) Acesse a URL abaixo em um navegador, faça login e autorize o acesso:")
    print()
    print(f"   {url}")
    print()
    print("2) Após o redirecionamento, copie o valor do parâmetro 'code' da URL.")
    print("3) Abra um shell Python e execute algo como:")
    print()
    print("   >>> from auth_manual import exchange_code_for_tokens")
    print("   >>> from settings import load_config")
    print("   >>> config = load_config()")
    print("   >>> exchange_code_for_tokens('SEU_CODE_AQUI', config)")
    print()
    print("Isso irá criar/atualizar o arquivo tiny_tokens.json na pasta do projeto.")
    print("=" * 72)


def run_examples() -> None:
    """
    Executa os exemplos básicos de extração.
    """
    print("Iniciando extração de pedidos (mês atual e mês anterior)...")
    extract_pedidos_months_example()

    print()
    print("Iniciando extração de produtos (estoque completo)...")
    extract_produtos_example()


if __name__ == "__main__":
    run_examples()

