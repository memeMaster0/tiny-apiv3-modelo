"""
Autenticação opcional com Selenium.

Este módulo NÃO é obrigatório para usar o template.
Ele apenas ajuda a obter o `code` automaticamente, abrindo o navegador.

Requisitos extras (veja requirements.txt):
- selenium
- webdriver-manager
"""

from __future__ import annotations

from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs

from settings import TinyConfig
from auth_manual import generate_auth_url


def get_code_with_selenium(config: TinyConfig, timeout: int = 60) -> str:
    """
    Abre o navegador, faz o fluxo de login e devolve o `code` encontrado na URL final.

    Esta função é um exemplo. Dependendo de como é a tela de login da sua conta,
    você pode precisar adaptar os seletores.
    """
    chrome_options = Options()
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        auth_url = generate_auth_url(config)
        driver.get(auth_url)

        wait = WebDriverWait(driver, 30)

        # login simples baseado em campos username/password padrões do Keycloak
        if config.tiny_username:
            username = wait.until(EC.presence_of_element_located((By.ID, "username")))
            username.clear()
            username.send_keys(config.tiny_username)

        if config.tiny_password:
            password = wait.until(EC.presence_of_element_located((By.ID, "password")))
            password.clear()
            password.send_keys(config.tiny_password)

        # botão de login padrão
        try:
            login_button = driver.find_element(By.ID, "kc-login")
        except Exception:
            login_button = None

        if login_button:
            login_button.click()

        # espera até aparecer ?code= na URL de redirecionamento
        wait = WebDriverWait(driver, timeout)

        def url_has_code(driver_obj) -> bool:
            return "code=" in driver_obj.current_url

        wait.until(url_has_code)

        current_url = driver.current_url
        parsed = urlparse(current_url)
        query = parse_qs(parsed.query)
        code_values = query.get("code")
        if not code_values:
            raise RuntimeError("Parâmetro 'code' não encontrado na URL final.")

        return code_values[0]
    except TimeoutException as exc:
        raise RuntimeError("Timeout aguardando a autenticação no Tiny via Selenium.") from exc
    finally:
        driver.quit()

