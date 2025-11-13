"""
Utilidades gerais do projeto.
"""

import pandas as pd


def ordenar_fundos(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(by=["score", "dy_pct"], ascending=[False, False])
