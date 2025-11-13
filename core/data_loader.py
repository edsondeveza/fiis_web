"""
Carregamento de dados: Excel ou Fundamentus Online
Python 3.12
"""

import pandas as pd
import requests
from pathlib import Path

URL_FUNDAMENTUS = "https://www.fundamentus.com.br/fii_resultado.php"


def carregar_excel(caminho: Path) -> pd.DataFrame:
    """Carrega o Excel exportado manualmente pelo usuário."""
    return pd.read_excel(caminho)


def carregar_fundamentus_online() -> pd.DataFrame:
    """Baixa FIIs diretamente do Fundamentus."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(URL_FUNDAMENTUS, headers=headers, timeout=30)
    resp.raise_for_status()

    tabelas = pd.read_html(
        resp.text,
        decimal=",",
        thousands=".",
        encoding="utf-8",
    )
    return tabelas[0]
