"""
Módulo de pré-processamento dos dados de FIIs do Fundamentus.

Pensado para Python 3.12.
"""

from __future__ import annotations

import unicodedata
from typing import Any

import pandas as pd
import pandas.api.types as ptypes


def _remover_acentos(texto: str) -> str:
    """Remove acentos de um texto usando unicodedata."""
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza os nomes das colunas para um padrão mais fácil de usar no código:

    - tudo minúsculo
    - remove espaços extras
    - remove acentos
    - troca espaço por "_"
    - remove "%" dos nomes
    - troca "/" por "_"

    Exemplo:
        "Dividend Yield"   -> "dividend_yield"
        "Vacância Média"   -> "vacancia_media"
        "Valor de Mercado" -> "valor_de_mercado"
    """
    df = df.copy()

    novas_colunas: list[str] = []
    for col in df.columns:
        col_str = str(col).strip().lower()
        col_str = _remover_acentos(col_str)
        col_str = (
            col_str.replace(" ", "_")
            .replace("%", "")
            .replace("/", "_")
        )
        novas_colunas.append(col_str)

    df.columns = novas_colunas
    return df


def limpar_percentual(valor: Any) -> float | None:
    """
    Converte strings como '12,86%' em float fracionário 0.1286.

    Regras:
        - Se for NaN -> None
        - Se já for número -> retorna como float (assumindo que já é fração 0-1 ou valor adequado)
        - Se for string com vírgula e '%' (padrão Fundamentus), converte para fração.

    Exemplos:
        '12,86%' -> 0.1286
        '0,00%'  -> 0.0
    """
    if pd.isna(valor):
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()
    if not texto:
        return None

    # Remove símbolo de porcentagem
    texto = texto.replace("%", "")

    # Padrão do Fundamentus:
    # ponto como separador de milhar e vírgula como decimal
    # Ex.: '1.234,56' -> '1234.56'
    texto = texto.replace(".", "")
    texto = texto.replace(",", ".", 1)

    try:
        numero = float(texto)
    except ValueError:
        return None

    # Converte para fração (0-1)
    return numero / 100.0


def tratar_tipos_numericos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte colunas numéricas para float/int, tratando especialmente
    os campos que vêm como texto do Fundamentus.

    - Percentuais (string com vírgula e '%'):
        ffo_yield, dividend_yield, cap_rate, vacancia_media
        Ex.: '13,63%' -> 0.1363

    - Colunas numéricas "normais" (cotação, P/VP, liquidez etc.) são convertidas com to_numeric.

    Após o tratamento, as colunas abaixo (se existirem) serão numéricas:

        - cotacao
        - ffo_yield
        - dividend_yield
        - p_vp
        - valor_de_mercado
        - liquidez
        - qtd_de_imoveis
        - preco_do_m2
        - aluguel_por_m2
        - cap_rate
        - vacancia_media
    """
    df = df.copy()

    # Colunas percentuais que vêm como texto com '%' e vírgula
    colunas_percentuais = [
        "ffo_yield",
        "dividend_yield",
        "cap_rate",
        "vacancia_media",
    ]

    for col in colunas_percentuais:
        if col in df.columns:
            df[col] = df[col].apply(limpar_percentual)

    # Colunas numéricas normais
    colunas_numericas = [
        "cotacao",
        "p_vp",
        "valor_de_mercado",
        "liquidez",
        "qtd_de_imoveis",
        "preco_do_m2",
        "aluguel_por_m2",
    ]

    for col in colunas_numericas:
        if col not in df.columns:
            continue

        # Se veio como texto, converte; se já é numérico, apenas garante
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remover linhas sem cotação (provavelmente inválidas)
    if "cotacao" in df.columns:
        df = df.dropna(subset=["cotacao"])

    return df


def criar_percentuais(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria colunas em % a partir das colunas fracionárias (0 a 1):

        - dy_pct: Dividend Yield em %
        - ffo_pct: FFO Yield em %
        - vacancia_pct: Vacância média em %

    Se alguma coluna base não existir, a coluna em % é criada como NA.
    """
    df = df.copy()

    if "dividend_yield" in df.columns:
        df["dy_pct"] = (df["dividend_yield"] * 100).round(2)
    else:
        df["dy_pct"] = pd.NA

    if "ffo_yield" in df.columns:
        df["ffo_pct"] = (df["ffo_yield"] * 100).round(2)
    else:
        df["ffo_pct"] = pd.NA

    if "vacancia_media" in df.columns:
        df["vacancia_pct"] = (df["vacancia_media"] * 100).round(2)
    else:
        df["vacancia_pct"] = pd.NA

    return df

def adicionar_macro_segmento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria uma coluna 'macro_segmento' com categorias mais gerais:
    - Papéis / CRI
    - Logístico
    - Shoppings
    - FOF
    - Lajes / Escritórios
    - Outros
    """
    df = df.copy()

    def classificar(seg: Any) -> str:
        s = str(seg).lower()

        if any(x in s for x in ["papel", "cri", "receb"]):
            return "Papéis / CRI"
        if "logist" in s:
            return "Logístico"
        if "shopp" in s:
            return "Shoppings"
        if any(x in s for x in ["fundo de fundos", "fii de fiis", "fundo de fii", "fof"]):
            return "FOF / FII de FIIs"
        if any(x in s for x in ["laje", "escritorio"]):
            return "Lajes / Escritórios"
        return "Outros"

    if "segmento" in df.columns:
        df["macro_segmento"] = df["segmento"].map(classificar)
    else:
        df["macro_segmento"] = "Desconhecido"

    return df
