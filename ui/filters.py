"""
Componentes de filtros para a sidebar.
"""

from __future__ import annotations

from typing import Tuple, List
import streamlit as st

from config import Config


def render_modo_selector() -> str:
    """Renderiza seletor de modo (Iniciante/Avançado)."""
    st.sidebar.header("🎛️ Modo de uso")

    modo = st.sidebar.radio(
        "Selecione o modo:",
        ["Iniciante", "Avançado"],
        help=(
            "Iniciante: parâmetros pré-configurados e mais simples.\n"
            "Avançado: liberdade total nos filtros."
        ),
    )

    return modo


def render_filtros_iniciante() -> Tuple[float, float, float, float, float, int]:
    """
    Renderiza filtros para modo iniciante.

    Returns:
        Tupla (min_dy, max_pvp, min_liq, max_vac, min_vm, min_score)
    """
    st.sidebar.header("⚙️ Regras de filtros")

    st.sidebar.markdown(
        "Modo indicado para quem está começando.\n\n"
        "Os parâmetros foram pensados para:\n"
        "- Foco em renda\n"
        "- Evitar FIIs muito pequenos\n"
        "- Evitar vacância alta\n"
        "- Evitar P/VP caro"
    )

    cfg = Config.filtros_iniciante

    min_dy = st.sidebar.number_input(
        "DY mínimo (%)",
        min_value=0.0,
        max_value=30.0,
        value=cfg.min_dy,
        step=0.5,
        help="Quanto maior, mais exigente. 8% ao ano é razoável.",
    )

    # Valores fixos no modo iniciante
    max_pvp = cfg.max_pvp
    min_liq = cfg.min_liq
    max_vac = cfg.max_vac
    min_vm = cfg.min_vm

    min_score = st.sidebar.slider(
        "Score mínimo",
        min_value=0,
        max_value=5,
        value=cfg.min_score,
        step=1,
        help=(
            "Quantos critérios o fundo precisa cumprir.\n"
            "0 = mostra todos após filtros básicos.\n"
            "3 = pelo menos 3 critérios ok."
        ),
    )

    # Mostra valores fixos
    st.sidebar.info(
        f"**Valores fixos neste modo:**\n\n"
        f"- P/VP máximo: {max_pvp}\n"
        f"- Liquidez mín.: R$ {min_liq:,.0f}\n"
        f"- Vacância máx.: {max_vac}%\n"
        f"- Valor mercado mín.: R$ {min_vm:,.0f}"
    )

    return min_dy, max_pvp, min_liq, max_vac, min_vm, min_score


def render_filtros_avancado() -> Tuple[float, float, float, float, float, int]:
    """
    Renderiza filtros para modo avançado.

    Returns:
        Tupla (min_dy, max_pvp, min_liq, max_vac, min_vm, min_score)
    """
    st.sidebar.header("⚙️ Regras de filtros")

    st.sidebar.markdown(
        "Modo avançado: filtros começam **abertos**.\n\n"
        "Aperte aos poucos até chegar numa lista enxuta."
    )

    cfg = Config.filtros_avancado

    min_dy = st.sidebar.number_input(
        "DY mínimo (%)",
        min_value=0.0,
        max_value=30.0,
        value=cfg.min_dy,
        step=0.5,
        help="Começa em 0%. Aumente para exigir mais renda.",
    )

    max_pvp = st.sidebar.number_input(
        "P/VP máximo",
        min_value=0.0,
        max_value=3.0,
        value=cfg.max_pvp,
        step=0.05,
        help="Começa em 3.0. Diminua para fundos mais baratos.",
    )

    min_liq = st.sidebar.number_input(
        "Liquidez mínima (R$/dia)",
        min_value=0.0,
        max_value=5_000_000.0,
        value=cfg.min_liq,
        step=10_000.0,
        help="Começa em 0. Aumente para evitar fundos pouco negociados.",
    )

    max_vac = st.sidebar.number_input(
        "Vacância máxima (%)",
        min_value=0.0,
        max_value=100.0,
        value=cfg.max_vac,
        step=5.0,
        help="Começa em 100%. Diminua para exigir menos vacância.",
    )

    min_vm = st.sidebar.number_input(
        "Valor de mercado mínimo (R$)",
        min_value=0.0,
        max_value=20_000_000_000.0,
        value=cfg.min_vm,
        step=50_000_000.0,
        help="Começa em 0. Aumente para evitar FIIs pequenos.",
    )

    min_score = st.sidebar.slider(
        "Score mínimo",
        min_value=0,
        max_value=5,
        value=cfg.min_score,
        step=1,
        help="Começa em 0. Suba para filtrar pelos critérios.",
    )

    return min_dy, max_pvp, min_liq, max_vac, min_vm, min_score


def render_filtros_segmento(
    macro_disponiveis: List[str],
    segmentos_disponiveis: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Renderiza filtros de macro-segmento e segmento.

    Returns:
        Tupla (macro_selecionados, segmentos_selecionados)
    """
    macro_sel = st.sidebar.multiselect(
        "Macro-segmento",
        options=macro_disponiveis,
        default=macro_disponiveis,
        help="Ex.: Papéis, Logístico, Shoppings"
    )

    segmentos_sel = st.sidebar.multiselect(
        "Segmentos (opcional)",
        options=segmentos_disponiveis,
        default=segmentos_disponiveis,
    )

    return macro_sel, segmentos_sel


def render_filtros_semelhanca(
    sugestao: dict,
    usar_sugestoes_default: bool = True
) -> Tuple[float, float, int, bool]:
    """
    Renderiza filtros para busca de semelhantes.

    Returns:
        Tupla (tol_dy, tol_pvp, min_liq, mesmo_segmento)
    """
    st.markdown(
        f"""
**Sugestão automática de parâmetros:**

- Tolerância DY: **± {sugestao['tol_dy']:.2f}%**
- Tolerância P/VP: **± {sugestao['tol_pvp']:.2f}**
- Liquidez mínima: **R$ {sugestao['min_liq']:,}** por dia
"""
    )

    usar_sugestoes = st.checkbox(
        "Usar parâmetros sugeridos automaticamente",
        value=usar_sugestoes_default,
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
            "Liquidez mín. (R$/dia)",
            min_value=0,
            max_value=5_000_000,
            value=int(sugestao["min_liq"]) if usar_sugestoes else 30_000,
            step=10_000,
        )

    mesmo_segmento = st.checkbox(
        "Buscar somente no mesmo segmento",
        value=True,
        help=(
            "Desmarque para procurar semelhantes em outros segmentos."
        ),
    )

    return tol_dy, tol_pvp, min_liq_sim, mesmo_segmento
