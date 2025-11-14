"""
Carregamento de dados com tratamento robusto de erros.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)


class DataLoaderError(Exception):
    """Exceção customizada para erros de carregamento."""
    pass


def carregar_excel(caminho: Path) -> pd.DataFrame:
    """
    Carrega Excel com tratamento de erros.

    Args:
        caminho: Path do arquivo Excel

    Returns:
        DataFrame com dados do Excel

    Raises:
        DataLoaderError: Se houver erro ao ler o arquivo
    """
    try:
        if not caminho.exists():
            raise DataLoaderError(f"Arquivo não encontrado: {caminho}")

        df = pd.read_excel(caminho)
        logger.info(f"Excel carregado: {len(df)} linhas de {caminho}")
        return df

    except Exception as e:
        logger.error(f"Erro ao carregar Excel: {e}")
        raise DataLoaderError(f"Erro ao ler Excel: {e}")


def carregar_fundamentus_online(
    url: str,
    user_agent: str,
    timeout: int = 30,
    max_retries: int = 3
) -> pd.DataFrame:
    """
    Baixa dados do Fundamentus com retry automático e tratamento de erros.

    Args:
        url: URL do Fundamentus
        user_agent: User-Agent para o request
        timeout: Timeout em segundos
        max_retries: Número máximo de tentativas

    Returns:
        DataFrame com dados dos FIIs

    Raises:
        DataLoaderError: Se não conseguir baixar após todas as tentativas
    """
    headers = {"User-Agent": user_agent}

    for tentativa in range(1, max_retries + 1):
        try:
            logger.info(
                f"Tentativa {tentativa}/{max_retries} de carregar Fundamentus")

            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()

            # Valida se recebeu HTML
            if not resp.text or len(resp.text) < 100:
                raise DataLoaderError("Resposta vazia do Fundamentus")

            # Parse HTML para DataFrame
            tabelas = pd.read_html(
                resp.text,
                decimal=",",
                thousands=".",
                encoding="utf-8",
            )

            if not tabelas:
                raise DataLoaderError("Nenhuma tabela encontrada no HTML")

            df = tabelas[0]
            logger.info(f"Fundamentus carregado: {len(df)} FIIs")

            return df

        except Timeout:
            logger.warning(f"Timeout na tentativa {tentativa}")
            if tentativa == max_retries:
                raise DataLoaderError(
                    "Timeout ao conectar ao Fundamentus. "
                    "O site pode estar lento. Tente novamente em alguns minutos."
                )

        except ConnectionError:
            logger.warning(f"Erro de conexão na tentativa {tentativa}")
            if tentativa == max_retries:
                raise DataLoaderError(
                    "Não foi possível conectar ao Fundamentus. "
                    "Verifique sua conexão com a internet."
                )

        except RequestException as e:
            logger.error(f"Erro de requisição: {e}")
            if tentativa == max_retries:
                raise DataLoaderError(
                    f"Erro ao acessar Fundamentus: {e}"
                )

        except ValueError as e:
            # Erro no parse do HTML
            logger.error(f"Erro ao fazer parse do HTML: {e}")
            raise DataLoaderError(
                "Erro ao processar dados do Fundamentus. "
                "O layout do site pode ter mudado."
            )

        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            if tentativa == max_retries:
                raise DataLoaderError(f"Erro inesperado: {e}")

    # Nunca deve chegar aqui, mas por segurança
    raise DataLoaderError("Falha ao carregar dados após todas as tentativas")


def verificar_saude_dados(df: pd.DataFrame) -> tuple[bool, Optional[str]]:
    """
    Verifica se os dados baixados têm qualidade mínima.

    Returns:
        Tupla (saude_ok: bool, mensagem: Optional[str])
    """
    if df.empty:
        return False, "DataFrame vazio"

    if len(df) < 10:
        return False, f"Apenas {len(df)} registros (esperado > 10)"

    # Verifica se tem colunas razoáveis
    colunas_esperadas_parciais = ["papel", "cotacao", "segmento"]
    colunas_presentes = [
        col for col in colunas_esperadas_parciais
        if any(col.lower() in str(c).lower() for c in df.columns)
    ]

    if len(colunas_presentes) < 2:
        return False, "Estrutura de dados inesperada"

    return True, None
