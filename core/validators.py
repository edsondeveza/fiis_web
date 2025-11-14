"""
Módulo de validação de dados para FIIs.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class ValidacaoError(Exception):
    """Exceção customizada para erros de validação."""
    pass


def validar_dataframe(
    df: pd.DataFrame,
    colunas_obrigatorias: List[str]
) -> Tuple[bool, List[str]]:
    """
    Valida se o DataFrame contém todas as colunas obrigatórias.
    
    Args:
        df: DataFrame a ser validado
        colunas_obrigatorias: Lista de colunas que devem existir
        
    Returns:
        Tupla (valido: bool, colunas_faltantes: List[str])
    """
    if df.empty:
        logger.warning("DataFrame vazio fornecido para validação")
        return False, []
    
    colunas_faltantes = [
        col for col in colunas_obrigatorias
        if col not in df.columns
    ]
    
    if colunas_faltantes:
        logger.error(f"Colunas faltantes: {colunas_faltantes}")
        return False, colunas_faltantes
    
    logger.info("DataFrame validado com sucesso")
    return True, []


def validar_filtros(
    min_dy: float,
    max_pvp: float,
    min_liq: float,
    max_vac: float,
    min_vm: float
) -> Tuple[bool, str]:
    """
    Valida se os filtros fazem sentido.
    
    Returns:
        Tupla (valido: bool, mensagem_erro: str)
    """
    if min_dy < 0:
        return False, "DY mínimo não pode ser negativo"
    
    if min_dy > 50:
        return False, "DY mínimo parece muito alto (> 50%)"
    
    if max_pvp < 0:
        return False, "P/VP máximo não pode ser negativo"
    
    if max_pvp > 10:
        return False, "P/VP máximo parece muito alto (> 10)"
    
    if min_liq < 0:
        return False, "Liquidez mínima não pode ser negativa"
    
    if max_vac < 0 or max_vac > 100:
        return False, "Vacância máxima deve estar entre 0 e 100%"
    
    if min_vm < 0:
        return False, "Valor de mercado mínimo não pode ser negativo"
    
    return True, ""


def validar_dados_fundamentus(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Valida se os dados do Fundamentus têm qualidade mínima.
    
    Returns:
        Tupla (valido: bool, mensagem: str)
    """
    if df.empty:
        return False, "DataFrame vazio retornado do Fundamentus"
    
    if len(df) < 10:
        return False, f"Apenas {len(df)} fundos encontrados (esperado > 10)"
    
    # Verifica se há pelo menos algumas cotações válidas
    if "cotacao" in df.columns:
        cotacoes_validas = df["cotacao"].notna().sum()
        if cotacoes_validas < 10:
            return False, f"Apenas {cotacoes_validas} cotações válidas"
    
    return True, f"{len(df)} fundos carregados com sucesso"


def sugerir_ajustes_filtros(df: pd.DataFrame, qtd_filtrados: int) -> str:
    """
    Sugere ajustes nos filtros baseado na quantidade de fundos filtrados.
    
    Args:
        df: DataFrame completo
        qtd_filtrados: Quantidade de fundos após filtros
        
    Returns:
        String com sugestões
    """
    total = len(df)
    percentual = (qtd_filtrados / total * 100) if total > 0 else 0
    
    if qtd_filtrados == 0:
        return (
            "⚠️ **Nenhum fundo encontrado!**\n\n"
            "Sugestões:\n"
            "- Diminua o **Score mínimo**\n"
            "- Reduza o **DY mínimo**\n"
            "- Aumente o **P/VP máximo**\n"
            "- Reduza a **Liquidez mínima**\n"
            "- Aumente a **Vacância máxima**"
        )
    
    if percentual < 1:
        return (
            "⚠️ **Filtros muito restritivos!**\n\n"
            f"Apenas {percentual:.1f}% dos fundos passaram.\n"
            "Considere relaxar alguns critérios."
        )
    
    if percentual > 80:
        return (
            "ℹ️ **Filtros muito abertos**\n\n"
            f"{percentual:.1f}% dos fundos passaram.\n"
            "Considere aumentar a exigência para uma seleção mais refinada."
        )
    
    return (
        f"✅ **Filtros equilibrados**: {percentual:.1f}% dos fundos selecionados"
    )
