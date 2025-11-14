"""
Testes unitários para o módulo de preprocessing.
"""

import pandas as pd
import pytest

from core.preprocessing import (
    normalizar_colunas,
    limpar_percentual,
    tratar_tipos_numericos,
    criar_percentuais,
    adicionar_macro_segmento,
)


class TestNormalizarColunas:
    """Testes para normalização de colunas."""
    
    def test_normaliza_colunas_simples(self):
        df = pd.DataFrame({"Dividend Yield": [1, 2], "P/VP": [3, 4]})
        resultado = normalizar_colunas(df)
        
        assert "dividend_yield" in resultado.columns
        assert "p_vp" in resultado.columns
    
    def test_remove_acentos(self):
        df = pd.DataFrame({"Vacância Média": [1, 2]})
        resultado = normalizar_colunas(df)
        
        assert "vacancia_media" in resultado.columns
    
    def test_remove_porcentagem(self):
        df = pd.DataFrame({"DY %": [1, 2]})
        resultado = normalizar_colunas(df)
        
        assert "dy_" in resultado.columns
    
    def test_mantem_dados_originais(self):
        df = pd.DataFrame({"Teste": [1, 2, 3]})
        resultado = normalizar_colunas(df)
        
        assert len(resultado) == 3
        assert resultado["teste"].tolist() == [1, 2, 3]


class TestLimparPercentual:
    """Testes para limpeza de valores percentuais."""
    
    def test_converte_percentual_simples(self):
        assert limpar_percentual("12,86%") == pytest.approx(0.1286)
    
    def test_converte_percentual_zero(self):
        assert limpar_percentual("0,00%") == 0.0
    
    def test_converte_percentual_alto(self):
        assert limpar_percentual("99,99%") == pytest.approx(0.9999)
    
    def test_retorna_none_para_nan(self):
        assert limpar_percentual(pd.NA) is None
        assert limpar_percentual(None) is None
    
    def test_retorna_float_para_numero(self):
        assert limpar_percentual(0.5) == 0.5
        assert limpar_percentual(10) == 10.0
    
    def test_retorna_none_para_string_vazia(self):
        assert limpar_percentual("") is None
        assert limpar_percentual("   ") is None
    
    def test_trata_formato_fundamentus(self):
        # Formato com ponto como separador de milhar
        assert limpar_percentual("1.234,56%") == pytest.approx(12.3456)


class TestTratarTiposNumericos:
    """Testes para conversão de tipos numéricos."""
    
    def test_converte_percentuais(self):
        df = pd.DataFrame({
            "dividend_yield": ["12,50%", "8,00%"],
            "cotacao": [100.50, 200.75]  # Cotação já como float
        })
        
        resultado = tratar_tipos_numericos(df)
        
        assert resultado["dividend_yield"].iloc[0] == pytest.approx(0.125)
        assert resultado["dividend_yield"].iloc[1] == pytest.approx(0.08)
    
    def test_converte_colunas_numericas(self):
        # Usa valores numéricos válidos que o pandas to_numeric aceita
        df = pd.DataFrame({
            "cotacao": [100.50, 200.75],  # Float válido
            "p_vp": [0.95, 1.20],         # Float válido
            "liquidez": [50000, 100000]   # Int válido
        })
        
        resultado = tratar_tipos_numericos(df)
        
        # Verifica se é numérico (aceita int, float, np.int64, np.float64)
        assert pd.api.types.is_numeric_dtype(resultado["cotacao"])
        assert pd.api.types.is_numeric_dtype(resultado["p_vp"])
        assert pd.api.types.is_numeric_dtype(resultado["liquidez"])
        assert len(resultado) == 2  # Nenhuma linha removida
    
    def test_converte_string_com_ponto_decimal(self):
        """Testa conversão de strings com ponto decimal (formato padrão)."""
        df = pd.DataFrame({
            "cotacao": [100.0, 200.0],
            "p_vp": ["0.95", "1.20"]  # String mas com ponto
        })
        
        resultado = tratar_tipos_numericos(df)
        
        assert isinstance(resultado["p_vp"].iloc[0], (int, float))
        assert resultado["p_vp"].iloc[0] == pytest.approx(0.95)
        assert resultado["p_vp"].iloc[1] == pytest.approx(1.20)
    
    def test_remove_linhas_sem_cotacao(self):
        df = pd.DataFrame({
            "cotacao": [100.0, None, 200.0],
            "papel": ["FII1", "FII2", "FII3"]
        })
        
        resultado = tratar_tipos_numericos(df)
        
        assert len(resultado) == 2
        assert "FII2" not in resultado["papel"].values




class TestCriarPercentuais:
    """Testes para criação de colunas percentuais."""
    
    def test_cria_dy_pct(self):
        df = pd.DataFrame({"dividend_yield": [0.10, 0.12]})
        resultado = criar_percentuais(df)
        
        assert "dy_pct" in resultado.columns
        assert resultado["dy_pct"].iloc[0] == 10.0
        assert resultado["dy_pct"].iloc[1] == 12.0
    
    def test_cria_vacancia_pct(self):
        df = pd.DataFrame({"vacancia_media": [0.05, 0.15]})
        resultado = criar_percentuais(df)
        
        assert "vacancia_pct" in resultado.columns
        assert resultado["vacancia_pct"].iloc[0] == 5.0
        assert resultado["vacancia_pct"].iloc[1] == 15.0
    
    def test_cria_na_quando_coluna_faltando(self):
        df = pd.DataFrame({"papel": ["FII1", "FII2"]})
        resultado = criar_percentuais(df)
        
        assert "dy_pct" in resultado.columns
        assert pd.isna(resultado["dy_pct"].iloc[0])


class TestAdicionarMacroSegmento:
    """Testes para classificação de macro-segmentos."""
    
    def test_classifica_papeis(self):
        df = pd.DataFrame({"segmento": ["Papel", "CRI"]})
        resultado = adicionar_macro_segmento(df)
        
        assert resultado["macro_segmento"].iloc[0] == "Papéis / CRI"
        assert resultado["macro_segmento"].iloc[1] == "Papéis / CRI"
    
    def test_classifica_logistico(self):
        # A função normaliza e busca por "logist" (sem acento)
        df = pd.DataFrame({"segmento": ["Logistica", "Galpões Logisticos"]})
        resultado = adicionar_macro_segmento(df)
        
        assert resultado["macro_segmento"].iloc[0] == "Logístico"
        assert resultado["macro_segmento"].iloc[1] == "Logístico"
    
    def test_classifica_shoppings(self):
        df = pd.DataFrame({"segmento": ["Shoppings"]})
        resultado = adicionar_macro_segmento(df)
        
        assert resultado["macro_segmento"].iloc[0] == "Shoppings"
    
    def test_classifica_fof(self):
        df = pd.DataFrame({"segmento": ["Fundo de Fundos"]})
        resultado = adicionar_macro_segmento(df)
        
        assert resultado["macro_segmento"].iloc[0] == "FOF / FII de FIIs"
    
    def test_classifica_lajes(self):
        df = pd.DataFrame({"segmento": ["Lajes Corporativas"]})
        resultado = adicionar_macro_segmento(df)
        
        assert resultado["macro_segmento"].iloc[0] == "Lajes / Escritórios"
    
    def test_classifica_outros(self):
        df = pd.DataFrame({"segmento": ["Híbrido"]})
        resultado = adicionar_macro_segmento(df)
        
        assert resultado["macro_segmento"].iloc[0] == "Outros"
    
    def test_trata_segmento_faltando(self):
        df = pd.DataFrame({"papel": ["FII1"]})
        resultado = adicionar_macro_segmento(df)
        
        assert resultado["macro_segmento"].iloc[0] == "Desconhecido"


# Executar testes
if __name__ == "__main__":
    pytest.main([__file__, "-v"])