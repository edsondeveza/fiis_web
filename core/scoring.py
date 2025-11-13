"""
Cálculo do score e criação das flags dos critérios de investimento.
"""

import pandas as pd


def aplicar_regras(df: pd.DataFrame,
                   min_dy: float,
                   max_pvp: float,
                   min_liq: float,
                   max_vac: float,
                   min_vm: float) -> pd.DataFrame:

    df = df.copy()

    df["dy_bom"] = df["dy_pct"] >= min_dy
    df["pvp_bom"] = df["p_vp"] <= max_pvp
    df["liquidez_ok"] = df["liquidez"] >= min_liq
    df["vacancia_ok"] = df["vacancia_pct"] <= max_vac
    df["tamanho_ok"] = df["valor_de_mercado"] >= min_vm

    colunas = ["dy_bom", "pvp_bom", "liquidez_ok", "vacancia_ok", "tamanho_ok"]
    df["score"] = df[colunas].sum(axis=1)

    return df
