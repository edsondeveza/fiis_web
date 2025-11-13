"""
Interface Streamlit para análise de FIIs usando Fundamentus (online)
Pensado para Python 3.12
"""

from __future__ import annotations

import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.data_loader import carregar_fundamentus_online
from core.preprocessing import (
    normalizar_colunas,
    tratar_tipos_numericos,
    criar_percentuais,
    adicionar_macro_segmento,
)
from core.scoring import aplicar_regras
from core.similarity import semelhantes, sugerir_parametros_semelhanca
from core.utils import ordenar_fundos


# ==============================
#  NOMES "BONITOS" PARA COLUNAS
# ==============================

NOMES_BONITOS = {
    "papel": "Fundo",
    "macro_segmento": "Macro Segmento",
    "segmento": "Segmento",
    "cotacao": "Cotação (R$)",
    "dy_pct": "Dividend Yield (%)",
    "p_vp": "P/VP",
    "liquidez": "Liquidez (R$/dia)",
    "vacancia_pct": "Vacância (%)",
    "valor_de_mercado": "Valor de Mercado (R$)",
    "score": "Score",
}


def aplicar_nomes_bonitos(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia colunas para exibição mais amigável ao usuário."""
    df = df.copy()
    colunas = {c: NOMES_BONITOS.get(c, c) for c in df.columns}
    df.rename(columns=colunas, inplace=True)
    return df


# ==============================
#  FUNÇÃO PRINCIPAL
# ==============================


def main() -> None:
    st.set_page_config(page_title="Análise de FIIs", layout="wide")
    st.title("📊 Análise de FIIs • Fundamentus + Python")

    st.markdown(
        "> ⚠️ Esta é uma ferramenta de **estudo** e apoio à análise. "
        "**Não é recomendação de investimento.**\n\n"
        "Os dados são carregados **diretamente do Fundamentus** sempre que você abre o app."
    )

    # ==============================
    #  CARREGAR DADOS (APENAS ONLINE)
    # ==============================
    with st.spinner("Baixando dados do Fundamentus..."):
        df_raw = carregar_fundamentus_online()

    # Pipeline de preparação
    df = normalizar_colunas(df_raw)
    df = tratar_tipos_numericos(df)
    df = criar_percentuais(df)
    df = adicionar_macro_segmento(df)

    if df.empty:
        st.error(
            "Nenhum dado válido após o tratamento. "
            "Pode ter havido mudança no layout do Fundamentus ou problema na leitura."
        )
        st.write("Prévia dos dados brutos:")
        st.dataframe(df_raw.head(), use_container_width=True)
        st.stop()

    total_fundos = len(df)
    segmentos_disponiveis = sorted(df["segmento"].dropna().unique().tolist())
    macro_disponiveis = sorted(df["macro_segmento"].dropna().unique().tolist())

    st.caption(f"Total de fundos carregados após tratamento: **{total_fundos}**")

    # ==============================
    #  DASHBOARD GERAL
    # ==============================
    st.subheader("📊 Visão geral do mercado (snapshot Fundamentus)")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("Total de FIIs", value=total_fundos)

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

    # ==============================
    #  EXPLICAÇÃO DO SCORE
    # ==============================
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

Você controla:
- os **limites** de cada critério (DY, P/VP, liquidez etc.)
- e o **score mínimo** que o fundo precisa ter.
        """
    )

    # ==============================
    #  MODO: INICIANTE x AVANÇADO
    # ==============================
    st.sidebar.header("🎛️ Modo de uso")
    modo = st.sidebar.radio(
        "Selecione o modo:",
        ["Iniciante", "Avançado"],
        help=(
            "Iniciante: usa parâmetros pré-configurados e mais simples.\n"
            "Avançado: você escolhe todos os filtros do zero."
        ),
    )

    st.sidebar.header("⚙️ Regras de filtros")

    if modo == "Iniciante":
        st.sidebar.markdown(
            "Modo indicado para quem está começando.\n\n"
            "Os parâmetros abaixo foram pensados para:\n"
            "- Foco em renda\n"
            "- Evitar FIIs muito pequenos\n"
            "- Evitar vacância muito alta\n"
            "- Evitar P/VP muito caro\n"
        )

        # Parâmetros simplificados (com defaults mais rígidos)
        min_dy = st.sidebar.number_input(
            "DY mínimo (%)",
            min_value=0.0,
            max_value=30.0,
            value=8.0,
            step=0.5,
            help="Quanto maior, mais exigente. 8% ao ano é um ponto de partida razoável.",
        )

        max_pvp = 1.20          # P/VP máximo
        min_liq = 20_000.0      # liquidez mínima (float)
        max_vac = 15.0          # vacância máxima (%)
        min_vm = 100_000_000.0  # valor de mercado mínimo (R$)

        min_score = st.sidebar.slider(
            "Score mínimo",
            min_value=0,
            max_value=5,
            value=0,   # começa zerado
            step=1,
            help=(
                "Quantos critérios o fundo precisa cumprir.\n"
                "0 = considera todos os fundos que passam pelos filtros básicos.\n"
                "3 = pelo menos 3 critérios ok, e assim por diante."
            ),
        )

        macro_sel = st.sidebar.multiselect(
            "Macro-segmento (ex.: Papéis, Logístico, Shoppings)",
            options=macro_disponiveis,
            default=macro_disponiveis,
        )

        segmentos_sel = st.sidebar.multiselect(
            "Segmentos (opcional)",
            options=segmentos_disponiveis,
            default=segmentos_disponiveis,
        )

    else:
        st.sidebar.markdown(
            "Modo avançado: todos os filtros começam bem **abertos**.\n\n"
            "Você vai **apertando aos poucos** até chegar em uma lista mais enxuta."
        )

        min_dy = st.sidebar.number_input(
            "DY mínimo (%)",
            min_value=0.0,
            max_value=30.0,
            value=0.0,
            step=0.5,
            help="Começa em 0%. Aumente se quiser exigir mais renda.",
        )
        max_pvp = st.sidebar.number_input(
            "P/VP máximo",
            min_value=0.0,
            max_value=3.0,
            value=3.0,
            step=0.05,
            help="Começa em 3.0 (bem aberto). Diminua para buscar fundos mais baratos.",
        )
        min_liq = st.sidebar.number_input(
            "Liquidez mínima (R$/dia)",
            min_value=0.0,
            max_value=5_000_000.0,
            value=0.0,
            step=10_000.0,
            help="Começa em 0. Aumente para evitar fundos pouco negociados.",
        )
        max_vac = st.sidebar.number_input(
            "Vacância máxima (%)",
            min_value=0.0,
            max_value=100.0,
            value=100.0,
            step=5.0,
            help="Começa em 100%. Diminua para exigir vacância menor.",
        )
        min_vm = st.sidebar.number_input(
            "Valor de mercado mínimo (R$)",
            min_value=0.0,
            max_value=20_000_000_000.0,
            value=0.0,
            step=50_000_000.0,
            help="Começa em 0. Aumente para evitar FIIs muito pequenos.",
        )
        min_score = st.sidebar.slider(
            "Score mínimo",
            min_value=0,
            max_value=5,
            value=0,   # começa zerado
            step=1,
            help="Começa em 0 (mostra tudo após os filtros escolhidos). Suba conforme quiser filtrar pelos critérios.",
        )

        macro_sel = st.sidebar.multiselect(
            "Macro-segmento (ex.: Papéis, Logístico, Shoppings)",
            options=macro_disponiveis,
            default=macro_disponiveis,
        )

        segmentos_sel = st.sidebar.multiselect(
            "Filtrar por segmento",
            options=segmentos_disponiveis,
            default=segmentos_disponiveis,
        )

    # ==============================
    #  APLICAR REGRAS E FILTRAR
    # ==============================
    df_regras = aplicar_regras(
        df,
        min_dy=min_dy,
        max_pvp=max_pvp,
        min_liq=min_liq,
        max_vac=max_vac,
        min_vm=min_vm,
    )

    if "macro_segmento" in df_regras.columns and macro_sel:
        df_regras = df_regras[df_regras["macro_segmento"].isin(macro_sel)]

    if segmentos_sel:
        df_regras = df_regras[df_regras["segmento"].isin(segmentos_sel)]

    df_regras = ordenar_fundos(df_regras)

    filtrados = df_regras[df_regras["score"] >= min_score].copy()
    qtd_filtrados = len(filtrados)

    # ==============================
    #  RESULTADO PRINCIPAL
    # ==============================
    st.subheader("🎯 Fundos filtrados")

    st.markdown(
        f"""
**Modo:** `{modo}`  

- Fundos carregados (após tratamento): **{total_fundos}**  
- Fundos que passaram nos filtros atuais (score ≥ {min_score}): **{qtd_filtrados}**
"""
    )

    colunas_tabela = [
        "papel",
        "macro_segmento",
        "segmento",
        "cotacao",
        "dy_pct",
        "p_vp",
        "liquidez",
        "vacancia_pct",
        "valor_de_mercado",
        "score",
    ]

    if filtrados.empty:
        st.warning(
            "Nenhum fundo passou nas regras atuais.\n\n"
            "Sugestões:\n"
            "- Diminua o **Score mínimo** (ex.: de 3 para 2 ou 1)\n"
            "- Reduza o **DY mínimo** ou aumente o **P/VP máximo**\n"
            "- Aumente a vacância máxima ou diminua o valor de mercado mínimo\n"
        )
    else:
        tabela_bonita = aplicar_nomes_bonitos(filtrados[colunas_tabela])
        st.dataframe(
            tabela_bonita.reset_index(drop=True),
            use_container_width=True,
        )

        # ==============================
        #  EXPORTAR FILTRADOS
        # ==============================
        st.markdown("### 💾 Exportar FIIs filtrados")

        col_exp1, col_exp2 = st.columns(2)

        # CSV
        csv_bytes = filtrados[colunas_tabela].to_csv(index=False).encode(
            "utf-8-sig"
        )
        with col_exp1:
            st.download_button(
                label="⬇️ Baixar CSV",
                data=csv_bytes,
                file_name="fiis_filtrados.csv",
                mime="text/csv",
            )

        # Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            filtrados[colunas_tabela].to_excel(
                writer, index=False, sheet_name="FIIs_Filtrados"
            )
        buffer.seek(0)

        with col_exp2:
            st.download_button(
                label="⬇️ Baixar Excel",
                data=buffer,
                file_name="fiis_filtrados.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )

    # ==============================
    #  FUNDOS SEMELHANTES
    # ==============================
    st.subheader("🧬 Fundos semelhantes a um fundo alvo")

    if not df_regras.empty:
        papel_alvo = st.selectbox(
            "Escolha o fundo alvo:",
            df_regras["papel"].sort_values().unique(),
            help="O app procura fundos com DY, P/VP e liquidez parecidos com o fundo escolhido.",
        )

        sugestao = sugerir_parametros_semelhanca(df_regras, papel_alvo)

        st.markdown(
            f"""
**Sugestão automática de parâmetros** (baseada em segmento e DY do fundo **{papel_alvo}**):

- Tolerância DY: **± {sugestao['tol_dy']:.2f}%**
- Tolerância P/VP: **± {sugestao['tol_pvp']:.2f}**
- Liquidez mínima: **R$ {sugestao['min_liq']:,}** por dia
"""
        )

        usar_sugestoes = st.checkbox(
            "Usar parâmetros sugeridos automaticamente",
            value=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            tol_dy = st.number_input(
                "Tolerância DY (±%)",
                min_value=0.5,
                max_value=20.0,
                value=float(sugestao["tol_dy"]) if usar_sugestoes else 4.0,
                step=0.5,
            )
        with col2:
            tol_pvp = st.number_input(
                "Tolerância P/VP (±)",
                min_value=0.01,
                max_value=1.0,
                value=float(sugestao["tol_pvp"]) if usar_sugestoes else 0.20,
                step=0.01,
            )
        with col3:
            min_liq_sim = st.number_input(
                "Liquidez mínima p/ similares (R$/dia)",
                min_value=0,
                max_value=5_000_000,
                value=int(sugestao["min_liq"]) if usar_sugestoes else 30_000,
                step=10_000,
            )

        mesmo_segmento = st.checkbox(
            "Buscar somente no mesmo segmento do fundo alvo",
            value=True,
            help=(
                "Desmarque para procurar semelhantes mesmo em outros segmentos "
                "(útil quando o segmento do fundo alvo está estranho nos dados)."
            ),
        )

        if st.button("🔍 Buscar semelhantes"):
            df_alvo = df_regras[df_regras["papel"] == papel_alvo]
            if df_alvo.empty:
                st.error("Fundo alvo não encontrado depois dos filtros.")
                return

            alvo = df_alvo.iloc[0]

            sims = semelhantes(
                df_regras,
                papel=papel_alvo,
                tol_dy=tol_dy,
                tol_pvp=tol_pvp,
                min_liq=int(min_liq_sim),
                mesmo_segmento=mesmo_segmento,
            )

            qtd_sims = len(sims)
            st.markdown(
                f"Fundos semelhantes encontrados para **{papel_alvo}**: **{qtd_sims}**"
            )

            if sims.empty:
                st.info(
                    "Nenhum fundo atendeu aos critérios de similaridade.\n\n"
                    "Sugestões:\n"
                    "- Aumentar as tolerâncias de DY e P/VP\n"
                    "- Diminuir a liquidez mínima\n"
                    "- Desmarcar a opção 'mesmo segmento'."
                )
            else:
                colunas_sims = ["papel", "segmento", "dy_pct", "p_vp", "liquidez", "score"]
                tabela_sims = aplicar_nomes_bonitos(sims[colunas_sims])

                st.dataframe(
                    tabela_sims.reset_index(drop=True),
                    use_container_width=True,
                )

                # ==============================
                #  EXPORTAR SEMELHANTES
                # ==============================
                st.markdown("### 💾 Exportar FIIs semelhantes")

                col_s1, col_s2 = st.columns(2)

                csv_sims = sims[colunas_sims].to_csv(index=False).encode(
                    "utf-8-sig"
                )
                with col_s1:
                    st.download_button(
                        "⬇️ Baixar CSV (semelhantes)",
                        data=csv_sims,
                        file_name=f"fiis_semelhantes_{papel_alvo}.csv",
                        mime="text/csv",
                    )

                buffer_s = io.BytesIO()
                with pd.ExcelWriter(buffer_s, engine="openpyxl") as writer:
                    sims[colunas_sims].to_excel(
                        writer, index=False, sheet_name="Semelhantes"
                    )
                buffer_s.seek(0)

                with col_s2:
                    st.download_button(
                        "⬇️ Baixar Excel (semelhantes)",
                        data=buffer_s,
                        file_name=f"fiis_semelhantes_{papel_alvo}.xlsx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        ),
                    )

                # ==============================
                #  EXPLICAÇÃO DOS CRITÉRIOS
                # ==============================
                st.markdown("### 🧾 Como os semelhantes foram escolhidos")

                dy_min = alvo["dy_pct"] - tol_dy
                dy_max = alvo["dy_pct"] + tol_dy
                pvp_min = alvo["p_vp"] - tol_pvp
                pvp_max = alvo["p_vp"] + tol_pvp

                st.markdown(
                    f"""
Estou procurando FIIs com as seguintes características:

- DY entre **{dy_min:.2f}%** e **{dy_max:.2f}%**  
- P/VP entre **{pvp_min:.2f}** e **{pvp_max:.2f}**  
- Liquidez diária **mínima de R$ {int(min_liq_sim):,}**  
- Segmento: **{'mesmo segmento do alvo' if mesmo_segmento else 'qualquer segmento'}**
"""
                )

                st.markdown("#### Detalhes dos primeiros semelhantes:")

                for _, row in sims.head(5).iterrows():
                    delta_dy = row["dy_pct"] - alvo["dy_pct"]
                    delta_pvp = row["p_vp"] - alvo["p_vp"]

                    st.markdown(
                        f"- **{row['papel']}** ({row['segmento']}): "
                        f"DY {row['dy_pct']:.2f}% "
                        f"({delta_dy:+.2f} p.p. em relação a {papel_alvo}), "
                        f"P/VP {row['p_vp']:.2f} ({delta_pvp:+.2f}), "
                        f"liquidez R$ {row['liquidez']:,}, score {row['score']}"
                    )

                # ==============================
                #  RADAR CHART
                # ==============================
                st.markdown("### 🕸 Comparação visual (radar)")

                max_semelhantes = min(5, len(sims))
                qtd_no_radar = st.slider(
                    "Quantidade de FIIs semelhantes no gráfico",
                    min_value=1,
                    max_value=max_semelhantes,
                    value=max_semelhantes,
                )

                df_radar = pd.concat(
                    [df_alvo, sims.head(qtd_no_radar)],
                    ignore_index=True,
                )

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
                        norm_data.append([0.0] * len(df_radar))
                        continue

                    serie = df_radar[col].astype(float)
                    min_val = serie.min()
                    max_val = serie.max()

                    if max_val == min_val:
                        # Tudo igual → coloca tudo como 1.0 (todo mundo "igual")
                        norm = [1.0] * len(serie)
                    else:
                        # Normaliza 0–1
                        norm = (serie - min_val) / (max_val - min_val)
                        if not melhor_maior:
                            norm = 1 - norm

                    # Garante que norm seja sempre uma lista
                    if hasattr(norm, "tolist"):
                        norm_lista = norm.tolist()
                    else:
                        norm_lista = list(norm)

                    norm_data.append(norm_lista)

                # Transpor para lista por fundo
                valores_por_fundo = list(zip(*norm_data))

                fig = go.Figure()

                for nome, valores in zip(nomes, valores_por_fundo):
                    fig.add_trace(
                        go.Scatterpolar(
                            r=list(valores) + [valores[0]],
                            theta=categorias + [categorias[0]],
                            name=nome,
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
                )

                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
