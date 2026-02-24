## Template de Requisição à API v3 do Tiny

Template em Python para consumir a API v3 do Tiny ERP de forma simples e reutilizável.

O objetivo é servir como **modelo**: você clona o repositório, preenche o `.env`,
escolhe os endpoints e parâmetros, e já consegue gerar relatórios Excel a partir
dos dados retornados pela API.

### Funcionalidades principais

- **Autenticação OAuth 2.0 (Tiny v3)** com:
  - Fluxo **manual** (recomendado como base do template).
  - Fluxo **opcional com Selenium** para automatizar a coleta do `code`.
- **Cliente HTTP genérico** para a API v3 (`tiny_client.py`), com:
  - Paginação via `offset` e `limit`.
  - Tratamento básico de erros (401, 429, 4xx/5xx).
- **Camada de relatórios** (`reporting.py`):
  - Normalização dos dados com `pandas.json_normalize`.
  - Geração de arquivos Excel (`.xlsx`).
- **Exemplos prontos** em `examples/`:
  - `/pedidos`: mês atual e mês anterior.
  - `/produtos`: base completa de produtos/estoque.

---

## Estrutura do template

```text
modelo-apiv3-tiny/
├── auth_manual.py        # Fluxo de autenticação manual (obrigatório)
├── auth_selenium.py      # Fluxo opcional com Selenium (automatiza o CODE)
├── main.py               # Ponto de entrada com exemplos prontos
├── reporting.py          # Funções para DataFrame/Excel
├── settings.py           # Carrega .env e centraliza configuração
├── tiny_client.py        # Cliente HTTP genérico para a API v3
├── .env.example          # Modelo de variáveis de ambiente
├── requirements.txt      # Dependências (Selenium é opcional)
├── .gitignore            # Ignora .env, tiny_tokens.json, venv etc.
└── examples/
    ├── __init__.py
    ├── pedidos_exemplo.py   # Exemplo de extração de /pedidos
    └── produtos_exemplo.py  # Exemplo de extração de /produtos
```

---

## Pré-requisitos

- Python 3.10+ (recomendado).
- Conta Tiny ERP com acesso à API v3.
- Uma aplicação OAuth cadastrada no painel de desenvolvedores do Tiny.

### Criar e ativar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

Se quiser usar o fluxo com Selenium:

```bash
pip install selenium webdriver-manager
```

---

## Configuração do .env

Na pasta `modelo-apiv3-tiny/`, copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:

```env
TINY_CLIENT_ID=seu_client_id_aqui
TINY_CLIENT_SECRET=seu_client_secret_aqui
TINY_REDIRECT_URI=https://sua-url-de-retorno.com/

# (Opcional) Apenas se usar auth_selenium.py
TINY_USERNAME=seu_usuario_tiny
TINY_PASSWORD=sua_senha_tiny

REPORTS_PEDIDOS_DIR=./relatorios/pedidos
REPORTS_PRODUTOS_DIR=./relatorios/produtos
```

> **Importante:** O `TINY_REDIRECT_URI` deve ser exatamente o mesmo
> configurado na aplicação OAuth no painel do Tiny.

---

## Fluxo de autenticação

### 1. Fluxo manual (recomendado para o template)

1. Garanta que o `.env` está configurado.
2. Gere a URL de autorização:

   ```bash
   python -c "from settings import load_config; from auth_manual import generate_auth_url; c=load_config(); print(generate_auth_url(c))"
   ```

3. Acesse a URL no navegador, faça login e autorize o acesso.
4. Após o redirecionamento, copie o valor do parâmetro `code` da URL (tudo após `code=`).
5. Troque o `code` por tokens, salvando em `tiny_tokens.json`:

   ```bash
   python -c "from settings import load_config; from auth_manual import exchange_code_for_tokens; c=load_config(); exchange_code_for_tokens('SEU_CODE_AQUI', c)"
   ```

- O arquivo `tiny_tokens.json` será criado na pasta do template.
- O módulo `auth_manual.py` cuida automaticamente de:
  - Verificar se o `access_token` ainda é válido.
  - Renovar com `refresh_token` quando necessário.

Quando o `refresh_token` expirar, repita o processo (gerar nova URL, novo `code` e chamar `exchange_code_for_tokens`).

### 2. Fluxo opcional com Selenium

Se preferir automatizar a etapa de pegar o `code`, você pode usar `auth_selenium.py`
como base. Ele:

- Gera a URL de autorização.
- Abre o navegador.
- Preenche usuário/senha (se definidos no `.env`).
- Espera o redirecionamento e extrai o `code` da URL.

Este módulo é propositalmente simples e pode precisar de ajustes nos seletores
de elementos de tela, dependendo da sua conta/tema de login.

---

## Executando os exemplos

Depois de configurar o `.env` e gerar/salvar os tokens em `tiny_tokens.json`,
basta rodar:

```bash
python main.py
```

O `main.py` irá:

- Executar o exemplo de `/pedidos` (`examples/pedidos_exemplo.py`):
  - Mês atual.
  - Mês anterior.
- Executar o exemplo de `/produtos` (`examples/produtos_exemplo.py`):
  - Estoque completo.

Os arquivos serão salvos nas pastas definidas por:

- `REPORTS_PEDIDOS_DIR`
- `REPORTS_PRODUTOS_DIR`

no seu `.env`.

---

## Adaptando para outros endpoints

O módulo `tiny_client.py` expõe a função:

```python
from tiny_client import get_paginated

dados = get_paginated(
    endpoint="NOME_DO_ENDPOINT",
    params={"chave": "valor"},      # filtros opcionais
    entity_key="nome_da_lista",     # ex.: "pedidos", "produtos", "items"
)
```

Com ela você pode:

- Criar novos scripts em `examples/` para qualquer endpoint disponível na API v3.
- Definir os parâmetros de filtro (`params`) como datas, status etc.
- Reaproveitar o `reporting.to_excel()` para gerar relatórios.

Exemplo genérico:

```python
from settings import load_config
from tiny_client import get_paginated
from reporting import to_excel


def extrair_meu_endpoint():
    config = load_config()
    dados = get_paginated(
        "meu-endpoint",
        params={"algumParametro": "valor"},
        entity_key="itens",
        config=config,
    )
    caminho = to_excel(dados, "./relatorios/meu-endpoint", "meu_relatorio.xlsx")
    print(f"Relatório gerado em: {caminho}")
```

---

## Boas práticas e segurança

- **Nunca** versione:
  - `.env`
  - `tiny_tokens.json`
- O `.gitignore` já está configurado para ignorar esses arquivos dentro do template.
- Não compartilhe seu `CLIENT_SECRET`, tokens ou o arquivo `tiny_tokens.json`.
- Se precisar de logs mais detalhados, adicione prints localmente, mas evite
exibir tokens completos no console.

---

## Licença e uso

Este diretório foi pensado como um **modelo genérico** de integração com a
API v3 do Tiny. Você pode:

- Copiar a pasta `modelo-apiv3-tiny` para outro repositório.
- Adaptar nomes de arquivos, caminhos de relatórios e exemplos.
- Compartilhar o template em um repositório público, desde que não inclua
seus dados sensíveis (`.env`, `tiny_tokens.json` etc.).

