"""
Módulo de similaridade entre FIIs.

Pensado para Python 3.12.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd


def sugerir_parametros_semelhanca(
    df: pd.DataFrame,
    papel: str,
) -> Dict[str, float]:
    """
    Sugere parâmetros "inteligentes" de similaridade com base no fundo alvo.

    Leva em conta:
        - Segmento (papel, logístico, shopping, FOF etc.)
        - DY do fundo alvo (dy_pct)

    Retorna:
        {
            "tol_dy": float,   # tolerância de DY em pontos percentuais
            "tol_pvp": float,  # tolerância de P/VP
            "min_liq": int,    # liquidez mínima em R$/dia
        }
    """
    # valores padrão "equilibrados"
    tol_dy = 4.0
    tol_pvp = 0.20
    min_liq = 30_000

    df_alvo = df[df["papel"] == papel]

    if df_alvo.empty:
        return {
            "tol_dy": tol_dy,
            "tol_pvp": tol_pvp,
            "min_liq": min_liq,
        }

    alvo = df_alvo.iloc[0]
    segmento = str(alvo.get("segmento", "")).lower()
    dy = float(alvo.get("dy_pct") or 0.0)

    # Ajuste por segmento
    # Lembrando que os nomes vêm do Fundamentus e já normalizados no preprocessing
    if any(p in segmento for p in ["papel", "cri", "receb"]):
        # Fundos de papéis / CRI tendem a ter DY mais alto e mais volátil
        tol_dy = 6.0
        tol_pvp = 0.25
        min_liq = 20_000
    elif any(p in segmento for p in ["logist", "shopp", "laje", "renda_urbana"]):
        # Tijolo mais "redondinho"
        tol_dy = 3.0
        tol_pvp = 0.15
        min_liq = 40_000
    elif any(p in segmento for p in ["fundo_de_fundos", "fii_de_fiis", "fii_de_fii"]):
        # FOFs
        tol_dy = 4.0
        tol_pvp = 0.20
        min_liq = 25_000

    # Ajuste fino pelo DY do alvo (casos extremos)
    if dy >= 12.0:
        # DY muito alto → precisa tolerância maior
        tol_dy = max(tol_dy, 6.0)
    elif 0 < dy <= 7.0:
        # DY mais baixo → dá para ser um pouco mais rígido
        tol_dy = min(tol_dy, 3.0)

    return {
        "tol_dy": float(tol_dy),
        "tol_pvp": float(tol_pvp),
        "min_liq": int(min_liq),
    }


def semelhantes(
    df: pd.DataFrame,
    papel: str,
    tol_dy: float,
    tol_pvp: float,
    min_liq: int,
    mesmo_segmento: bool = True,
) -> pd.DataFrame:
    """
    Retorna fundos semelhantes ao fundo informado.

    Critérios de similaridade:
        - (opcional) mesmo segmento do fundo alvo
        - DY dentro de ±tol_dy
        - P/VP dentro de ±tol_pvp
        - Liquidez mínima >= min_liq

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os fundos já tratados.
        papel (str): Código do fundo alvo (ex: "MXRF11").
        tol_dy (float): Tolerância de DY em pontos percentuais.
        tol_pvp (float): Tolerância de P/VP.
        min_liq (int): Liquidez mínima em R$/dia.
        mesmo_segmento (bool): Se True, restringe ao mesmo segmento do alvo.

    Retorno:
        pd.DataFrame: DataFrame contendo os fundos mais parecidos.
    """
    df_alvo = df[df["papel"] == papel]

    if df_alvo.empty:
        raise ValueError(f"O fundo '{papel}' não foi encontrado no DataFrame.")

    alvo = df_alvo.iloc[0]

    dy_alvo = float(alvo.get("dy_pct") or 0.0)
    pvp_alvo = float(alvo.get("p_vp") or 0.0)
    segmento_alvo = alvo.get("segmento")

    # Filtros básicos
    dy_proximo = (df["dy_pct"] - dy_alvo).abs() <= tol_dy
    pvp_proximo = (df["p_vp"] - pvp_alvo).abs() <= tol_pvp
    liquidez_ok = df["liquidez"] >= min_liq

    filtro = dy_proximo & pvp_proximo & liquidez_ok

    # Mesmo segmento (opcional)
    if mesmo_segmento and "segmento" in df.columns:
        filtro_segmento = df["segmento"] == segmento_alvo
        filtro = filtro & filtro_segmento

    similares = df[filtro].copy()

    # Remove o próprio fundo alvo da lista (se aparecer)
    similares = similares[similares["papel"] != papel]

    # Ordena por proximidade de DY e P/VP e por liquidez
    similares["diff_dy"] = (similares["dy_pct"] - dy_alvo).abs()
    similares["diff_pvp"] = (similares["p_vp"] - pvp_alvo).abs()

    similares = similares.sort_values(
        by=["diff_dy", "diff_pvp", "liquidez"],
        ascending=[True, True, False],
    )

    # Opcional: remove colunas auxiliares antes de retornar
    similares = similares.drop(columns=["diff_dy", "diff_pvp"])

    return similares
