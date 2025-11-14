"""
Componentes reutilizáveis de UI para o Streamlit.
"""

from __future__ import annotations

import io
from typing import List, Dict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import Config


def aplicar_nomes_bonitos(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia colunas para exibição mais amigável."""
    df = df.copy()
    colunas = {c: Config.NOMES_BONITOS.get(c, c) for c in df.columns}
    df.rename(columns=colunas, inplace=True)
    return df


def render_dashboard(df: pd.DataFrame) -> None:
    """Renderiza o dashboard com métricas gerais."""
    st.subheader("📊 Visão geral do mercado (snapshot Fundamentus)")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("Total de FIIs", value=len(df))

    with col_b:
        dy_medio = (
            f"{df['dy_pct'].mean():.2f}"
            if df["dy_pct"].notna().any()
            else "N/A"
        )
        st.metric("DY médio (%)", value=dy_medio)

    with col_c:
        pvp_medio = (
            f"{df['p_vp'].mean():.2f}"
            if df["p_vp"].notna().any()
            else "N/A"
        )
        st.metric("P/VP médio", value=pvp_medio)

    col_d, col_e = st.columns(2)

    with col_d:
        vac_medio = (
            f"{df['vacancia_pct'].mean():.2f}"
            if df["vacancia_pct"].notna().any()
            else "N/A"
        )
        st.metric("Vacância média (%)", value=vac_medio)

    with col_e:
        vm_total = df["valor_de_mercado"].sum()
        st.metric(
            "Valor de mercado total (R$)",
            value=f"{vm_total:,.0f}".replace(",", "."),
        )


def render_explicacao_score() -> None:
    """Renderiza explicação do sistema de score."""
    st.markdown(
        """
### ℹ️ Como funciona o *score* (0 a 5)

Para cada fundo, são avaliados 5 critérios:

1. **DY bom** – Dividend Yield acima do mínimo definido  
2. **P/VP bom** – Preço/Valor Patrimonial abaixo do máximo definido  
3. **Liquidez ok** – Negociação diária acima do mínimo  
4. **Vacância ok** – Vacância abaixo do máximo definido  
5. **Tamanho ok** – Valor de mercado acima do mínimo

Cada critério cumprido vale **1 ponto**:

- Score **0** → não cumpre nenhum critério  
- Score **3** → cumpre 3 dos 5  
- Score **5** → cumpre todos os 5 critérios  
        """
    )


def render_tabela_fiis(
    df: pd.DataFrame,
    colunas: List[str],
    label: str = "FIIs"
) -> None:
    """Renderiza tabela de FIIs com formatação."""
    if df.empty:
        st.warning(f"Nenhum {label} para exibir")
        return

    tabela_bonita = aplicar_nomes_bonitos(df[colunas])
    st.dataframe(
        tabela_bonita.reset_index(drop=True),
        use_container_width=True,
    )


def render_botoes_exportacao(
    df: pd.DataFrame,
    colunas: List[str],
    prefixo_arquivo: str = "fiis"
) -> None:
    """Renderiza botões de exportação CSV e Excel."""
    st.markdown("### 💾 Exportar dados")

    col1, col2 = st.columns(2)

    # CSV
    csv_bytes = df[colunas].to_csv(index=False).encode("utf-8-sig")
    with col1:
        st.download_button(
            label="⬇️ Baixar CSV",
            data=csv_bytes,
            file_name=f"{prefixo_arquivo}.csv",
            mime="text/csv",
        )

    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df[colunas].to_excel(
            writer, index=False, sheet_name="Dados"
        )
    buffer.seek(0)

    with col2:
        st.download_button(
            label="⬇️ Baixar Excel",
            data=buffer,
            file_name=f"{prefixo_arquivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def render_radar_chart(
    df_radar: pd.DataFrame,
    papel_alvo: str
) -> None:
    """Renderiza gráfico radar comparando FIIs."""
    metricas = {
        "dy_pct": ("DY (%)", True),
        "p_vp": ("P/VP (quanto menor, melhor)", False),
        "vacancia_pct": ("Vacância (%) (quanto menor, melhor)", False),
        "liquidez": ("Liquidez", True),
        "valor_de_mercado": ("Valor de mercado", True),
        "score": ("Score", True),
    }

    categorias = [v[0] for v in metricas.values()]
    norm_data = []
    nomes = df_radar["papel"].tolist()

    for col, (_, melhor_maior) in metricas.items():
        if col not in df_radar.columns:
            norm_data.append([0.5] * len(df_radar))
            continue

        serie = df_radar[col].astype(float)
        min_val = serie.min()
        max_val = serie.max()

        if max_val == min_val:
            # Se todos iguais, coloca 0.5 (meio do gráfico)
            norm = [0.5] * len(serie)
        else:
            norm = (serie - min_val) / (max_val - min_val)
            if not melhor_maior:
                norm = 1 - norm

        norm_lista = norm.tolist() if hasattr(norm, "tolist") else list(norm)
        norm_data.append(norm_lista)

    valores_por_fundo = list(zip(*norm_data))

    fig = go.Figure()

    for i, (nome, valores) in enumerate(zip(nomes, valores_por_fundo)):
        # Destaca o fundo alvo
        linha_width = 3 if nome == papel_alvo else 1

        fig.add_trace(
            go.Scatterpolar(
                r=list(valores) + [valores[0]],
                theta=categorias + [categorias[0]],
                name=nome,
                line=dict(width=linha_width),
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
            )
        ),
        showlegend=True,
        title=f"Comparação: {papel_alvo} vs Semelhantes"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_detalhes_semelhantes(
    sims: pd.DataFrame,
    alvo: pd.Series,
    papel_alvo: str,
    tol_dy: float,
    tol_pvp: float,
    min_liq: int,
    mesmo_segmento: bool
) -> None:
    """Renderiza detalhes dos fundos semelhantes."""
    st.markdown("### 🧾 Como os semelhantes foram escolhidos")

    dy_min = alvo["dy_pct"] - tol_dy
    dy_max = alvo["dy_pct"] + tol_dy
    pvp_min = alvo["p_vp"] - tol_pvp
    pvp_max = alvo["p_vp"] + tol_pvp

    st.markdown(
        f"""
Critérios aplicados:

- DY entre **{dy_min:.2f}%** e **{dy_max:.2f}%**  
- P/VP entre **{pvp_min:.2f}** e **{pvp_max:.2f}**  
- Liquidez diária **≥ R$ {int(min_liq):,}**  
- Segmento: **{'mesmo do alvo' if mesmo_segmento else 'qualquer'}**
"""
    )

    st.markdown("#### 📋 Detalhes dos 5 primeiros:")

    for _, row in sims.head(5).iterrows():
        delta_dy = row["dy_pct"] - alvo["dy_pct"]
        delta_pvp = row["p_vp"] - alvo["p_vp"]

        st.markdown(
            f"- **{row['papel']}** ({row['segmento']}): "
            f"DY {row['dy_pct']:.2f}% "
            f"({delta_dy:+.2f} p.p.), "
            f"P/VP {row['p_vp']:.2f} ({delta_pvp:+.2f}), "
            f"liquidez R$ {row['liquidez']:,}, score {row['score']}"
        )
