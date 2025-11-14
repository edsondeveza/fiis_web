"""
Interface Streamlit para análise de FIIs - Versão Refatorada
"""

from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from config import Config
from core.data_loader import carregar_fundamentus_online, DataLoaderError
from core.preprocessing import (
    normalizar_colunas,
    tratar_tipos_numericos,
    criar_percentuais,
    adicionar_macro_segmento,
)
from core.scoring import aplicar_regras
from core.similarity import semelhantes, sugerir_parametros_semelhanca
from core.utils import ordenar_fundos
from core.validators import (
    validar_dataframe,
    validar_filtros,
    sugerir_ajustes_filtros,
)
from ui.components import (
    render_dashboard,
    render_explicacao_score,
    render_tabela_fiis,
    render_botoes_exportacao,
    render_radar_chart,
    render_detalhes_semelhantes,
)
from ui.filters import (
    render_modo_selector,
    render_filtros_iniciante,
    render_filtros_avancado,
    render_filtros_segmento,
    render_filtros_semelhanca,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@st.cache_data(ttl=Config.cache.ttl_seconds, show_spinner="🔄 Carregando dados do Fundamentus...")
def carregar_e_processar_dados() -> pd.DataFrame:
    """
    Carrega e processa dados do Fundamentus com cache e tratamento de erros.

    Returns:
        DataFrame processado e validado

    Raises:
        DataLoaderError: Se houver erro no carregamento ou validação
    """
    try:
        logger.info("Iniciando carregamento de dados")

        # Carrega dados
        df_raw = carregar_fundamentus_online(
            url=Config.fundamentus.url,
            user_agent=Config.fundamentus.user_agent,
            timeout=Config.fundamentus.timeout,
        )

        if df_raw.empty:
            raise DataLoaderError("DataFrame vazio retornado")

        logger.info(f"Dados brutos carregados: {len(df_raw)} linhas")

        # Pipeline de processamento
        df = normalizar_colunas(df_raw)
        df = tratar_tipos_numericos(df)
        df = criar_percentuais(df)
        df = adicionar_macro_segmento(df)

        # Validação
        valido, colunas_faltantes = validar_dataframe(
            df,
            Config.validacao.colunas_obrigatorias
        )

        if not valido:
            raise DataLoaderError(
                f"Colunas obrigatórias faltando: {colunas_faltantes}"
            )

        logger.info(f"Dados processados com sucesso: {len(df)} FIIs")
        return df

    except DataLoaderError:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado no processamento: {e}")
        raise DataLoaderError(f"Erro ao processar dados: {e}")


def renderizar_secao_filtrados(
    df_regras: pd.DataFrame,
    min_score: int,
    modo: str,
    total_fundos: int
) -> pd.DataFrame:
    """Renderiza a seção de fundos filtrados."""
    st.subheader("🎯 Fundos filtrados")

    filtrados = df_regras[df_regras["score"] >= min_score].copy()
    qtd_filtrados = len(filtrados)

    st.markdown(
        f"""
**Modo:** `{modo}`  

- Fundos carregados: **{total_fundos}**  
- Fundos que passaram (score ≥ {min_score}): **{qtd_filtrados}**
"""
    )

    # Sugestões de ajuste
    sugestao = sugerir_ajustes_filtros(df_regras, qtd_filtrados)
    st.info(sugestao)

    if filtrados.empty:
        st.warning(
            "Nenhum fundo passou nas regras atuais.\n\n"
            "Veja as sugestões acima para ajustar os filtros."
        )
    else:
        render_tabela_fiis(filtrados, Config.COLUNAS_TABELA)
        render_botoes_exportacao(
            filtrados,
            Config.COLUNAS_TABELA,
            "fiis_filtrados"
        )

    return filtrados


def renderizar_secao_semelhantes(df_regras: pd.DataFrame) -> None:
    """Renderiza a seção de busca de fundos semelhantes."""
    st.subheader("🧬 Fundos semelhantes a um fundo alvo")

    if df_regras.empty:
        st.warning("Nenhum fundo disponível para comparação")
        return

    papel_alvo = st.selectbox(
        "Escolha o fundo alvo:",
        df_regras["papel"].sort_values().unique(),
        help="O app busca fundos com características similares.",
    )

    # Sugestão de parâmetros
    sugestao = sugerir_parametros_semelhanca(df_regras, papel_alvo)

    # Renderiza filtros
    tol_dy, tol_pvp, min_liq_sim, mesmo_segmento = render_filtros_semelhanca(
        sugestao)

    if st.button("🔍 Buscar semelhantes"):
        df_alvo = df_regras[df_regras["papel"] == papel_alvo]

        if df_alvo.empty:
            st.error("Fundo alvo não encontrado")
            return

        alvo = df_alvo.iloc[0]

        try:
            sims = semelhantes(
                df_regras,
                papel=papel_alvo,
                tol_dy=tol_dy,
                tol_pvp=tol_pvp,
                min_liq=int(min_liq_sim),
                mesmo_segmento=mesmo_segmento,
            )

            qtd_sims = len(sims)
            st.success(f"✅ {qtd_sims} fundos semelhantes encontrados")

            if sims.empty:
                st.info(
                    "Nenhum fundo atendeu aos critérios.\n\n"
                    "Sugestões:\n"
                    "- Aumentar tolerâncias\n"
                    "- Diminuir liquidez mínima\n"
                    "- Desmarcar 'mesmo segmento'"
                )
            else:
                # Tabela
                render_tabela_fiis(
                    sims, Config.COLUNAS_SEMELHANTES, "semelhantes")

                # Exportação
                render_botoes_exportacao(
                    sims,
                    Config.COLUNAS_SEMELHANTES,
                    f"fiis_semelhantes_{papel_alvo}"
                )

                # Detalhes
                render_detalhes_semelhantes(
                    sims, alvo, papel_alvo, tol_dy, tol_pvp,
                    int(min_liq_sim), mesmo_segmento
                )

                # Radar
                st.markdown("### 🕸 Comparação visual (radar)")

                max_semelhantes = min(Config.ui.max_fiis_radar, len(sims))
                qtd_no_radar = st.slider(
                    "Quantidade de FIIs no gráfico",
                    min_value=1,
                    max_value=max_semelhantes,
                    value=max_semelhantes,
                )

                df_radar = pd.concat(
                    [df_alvo, sims.head(qtd_no_radar)],
                    ignore_index=True,
                )

                render_radar_chart(df_radar, papel_alvo)

        except Exception as e:
            logger.error(f"Erro ao buscar semelhantes: {e}")
            st.error(f"Erro ao buscar semelhantes: {e}")


def main() -> None:
    """Função principal da aplicação."""
    st.set_page_config(
        page_title=Config.ui.page_title,
        layout=Config.ui.layout
    )

    st.title("📊 Análise de FIIs • Fundamentus + Python")

    st.markdown(
        "> ⚠️ Ferramenta de **estudo** e apoio à análise. "
        "**Não é recomendação de investimento.**\n\n"
        "Dados carregados do Fundamentus em tempo real."
    )

    # ===== CARREGAMENTO DE DADOS =====
    try:
        df = carregar_e_processar_dados()
    except DataLoaderError as e:
        st.error(f"❌ {str(e)}")
        st.info(
            "**Possíveis causas:**\n"
            "- Site do Fundamentus fora do ar\n"
            "- Problema de conexão\n"
            "- Layout do site mudou\n\n"
            "Tente novamente em alguns minutos."
        )
        st.stop()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        st.error(f"❌ Erro inesperado: {e}")
        st.stop()

    total_fundos = len(df)
    segmentos_disponiveis = sorted(df["segmento"].dropna().unique().tolist())
    macro_disponiveis = sorted(df["macro_segmento"].dropna().unique().tolist())

    st.caption(f"Total de fundos carregados: **{total_fundos}**")

    # ===== DASHBOARD =====
    render_dashboard(df)

    # ===== EXPLICAÇÃO DO SCORE =====
    render_explicacao_score()

    # ===== FILTROS =====
    modo = render_modo_selector()

    if modo == "Iniciante":
        min_dy, max_pvp, min_liq, max_vac, min_vm, min_score = render_filtros_iniciante()
    else:
        min_dy, max_pvp, min_liq, max_vac, min_vm, min_score = render_filtros_avancado()

    # Validação dos filtros
    valido, msg_erro = validar_filtros(
        min_dy, max_pvp, min_liq, max_vac, min_vm)
    if not valido:
        st.sidebar.error(f"⚠️ {msg_erro}")
        st.stop()

    # Filtros de segmento
    macro_sel, segmentos_sel = render_filtros_segmento(
        macro_disponiveis,
        segmentos_disponiveis
    )

    # ===== APLICAR REGRAS =====
    df_regras = aplicar_regras(
        df,
        min_dy=min_dy,
        max_pvp=max_pvp,
        min_liq=min_liq,
        max_vac=max_vac,
        min_vm=min_vm,
    )

    # Filtrar por segmento
    if "macro_segmento" in df_regras.columns and macro_sel:
        df_regras = df_regras[df_regras["macro_segmento"].isin(macro_sel)]

    if segmentos_sel:
        df_regras = df_regras[df_regras["segmento"].isin(segmentos_sel)]

    df_regras = ordenar_fundos(df_regras)

    # ===== SEÇÃO DE FILTRADOS =====
    filtrados = renderizar_secao_filtrados(
        df_regras, min_score, modo, total_fundos)

    # ===== SEÇÃO DE SEMELHANTES =====
    if not df_regras.empty:
        renderizar_secao_semelhantes(df_regras)


if __name__ == "__main__":
    main()
