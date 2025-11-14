"""
Configurações centralizadas do projeto FIIs Web.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class FundamentusConfig:
    """Configurações de conexão com o Fundamentus."""
    url: str = "https://www.fundamentus.com.br/fii_resultado.php"
    timeout: int = 30
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )


@dataclass
class CacheConfig:
    """Configurações de cache."""
    ttl_seconds: int = 3600  # 1 hora
    show_spinner: bool = True


@dataclass
class FiltrosInicianteConfig:
    """Valores padrão para modo iniciante."""
    min_dy: float = 8.0
    max_pvp: float = 1.20
    min_liq: float = 20_000.0
    max_vac: float = 15.0
    min_vm: float = 100_000_000.0
    min_score: int = 0


@dataclass
class FiltrosAvancadoConfig:
    """Valores padrão para modo avançado."""
    min_dy: float = 0.0
    max_pvp: float = 3.0
    min_liq: float = 0.0
    max_vac: float = 100.0
    min_vm: float = 0.0
    min_score: int = 0


@dataclass
class ValidacaoConfig:
    """Configurações de validação."""
    colunas_obrigatorias: List[str] = None
    
    def __post_init__(self):
        if self.colunas_obrigatorias is None:
            self.colunas_obrigatorias = [
                "papel",
                "cotacao",
                "segmento",
                "p_vp",
                "liquidez",
                "valor_de_mercado"
            ]


@dataclass
class UIConfig:
    """Configurações de interface."""
    page_title: str = "Análise de FIIs"
    layout: str = "wide"
    max_fiis_radar: int = 5


class Config:
    """Configuração global da aplicação."""
    
    fundamentus = FundamentusConfig()
    cache = CacheConfig()
    filtros_iniciante = FiltrosInicianteConfig()
    filtros_avancado = FiltrosAvancadoConfig()
    validacao = ValidacaoConfig()
    ui = UIConfig()
    
    # Nomes amigáveis para colunas
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
    
    # Colunas para exibição em tabelas
    COLUNAS_TABELA = [
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
    
    COLUNAS_SEMELHANTES = [
        "papel",
        "segmento",
        "dy_pct",
        "p_vp",
        "liquidez",
        "score"
    ]
