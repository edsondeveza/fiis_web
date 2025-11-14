# 📊 FIIs Web — Análise Inteligente de Fundos Imobiliários (Python + Streamlit)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.51+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Uma aplicação web **profissional** e **robusta** para análise completa de **Fundos Imobiliários (FIIs)** com dados em tempo real do **Fundamentus**. Com filtros dinâmicos, dashboards interativos, sistema de scoring inteligente e busca de fundos semelhantes.

🆕 **Versão 2.0** - Totalmente refatorada com melhorias em performance, confiabilidade e experiência do usuário!

---

## ✨ O que há de novo na v2.0

### 🚀 Melhorias de Performance

- ✅ **Cache inteligente** de 1 hora para dados do Fundamentus
- ✅ Carregamento **3x mais rápido** após primeira execução
- ✅ Otimização do pipeline de processamento

### 🛡️ Confiabilidade

- ✅ **Tratamento robusto de erros** com retry automático
- ✅ **Validação completa** de dados em múltiplas camadas
- ✅ Mensagens de erro claras e acionáveis
- ✅ Fallback gracioso em caso de falhas

### 🎨 Experiência do Usuário

- ✅ **Sugestões inteligentes** de ajuste de filtros
- ✅ Loading indicators durante operações longas
- ✅ Feedback visual melhorado
- ✅ Interface mais responsiva

### 🏗️ Arquitetura

- ✅ **Código modular** e testável
- ✅ Separação clara entre UI e lógica de negócio
- ✅ Configurações centralizadas
- ✅ Logging estruturado
- ✅ **Testes unitários** incluídos

---

## 📌 Funcionalidades

### 🔎 Coleta Automática de Dados

- Scraping em tempo real do Fundamentus
- Retry automático em caso de falhas
- Cache inteligente para melhor performance
- Validação de qualidade dos dados

### 🎚 Dois Modos de Uso

**Modo Iniciante** 🔰

- Parâmetros pré-configurados
- Foco em fundos de qualidade
- Explicações detalhadas
- Ideal para começar

**Modo Avançado** 🔧

- Controle total sobre filtros
- Personalização completa
- Para investidores experientes

### 📊 Filtros Inteligentes

Configure até 7 parâmetros:

- DY mínimo (%)
- P/VP máximo
- Liquidez mínima (R$/dia)
- Vacância máxima (%)
- Valor de mercado mínimo (R$)
- Score mínimo (0-5)
- Macro-segmento e segmento

### 🧮 Sistema de Score (0-5)

Avaliação automática baseada em 5 critérios:

1. ✅ **DY bom** – Yield acima do mínimo
2. ✅ **P/VP bom** – Preço justo ou abaixo do VP
3. ✅ **Liquidez ok** – Volume de negociação adequado
4. ✅ **Vacância ok** – Ocupação saudável
5. ✅ **Tamanho ok** – Fundo com escala

### 🧬 Busca de Fundos Semelhantes

Sistema inteligente que:

- Sugere parâmetros automaticamente baseado no segmento
- Encontra FIIs com características similares
- Ordena por proximidade de DY e P/VP
- Permite ajuste fino dos critérios

### 🕸 Gráfico Radar Interativo

Compare visualmente até 5 fundos:

- DY
- P/VP
- Liquidez
- Vacância
- Valor de mercado
- Score

### 💾 Exportação de Dados

Exporte para:

- **CSV** (UTF-8 com BOM)
- **Excel** (.xlsx)

---

## 🏗 Arquitetura do Projeto

```
fiis_web/
│
├── app.py                      # Interface principal (orquestração)
├── config.py                   # Configurações centralizadas
│
├── core/                       # Lógica de negócio
│   ├── data_loader.py          # Carregamento com retry e validação
│   ├── preprocessing.py        # Pipeline de normalização
│   ├── scoring.py              # Sistema de pontuação
│   ├── similarity.py           # Algoritmo de similaridade
│   ├── utils.py                # Funções auxiliares
│   └── validators.py           # 🆕 Validações robustas
│
├── ui/                         # 🆕 Componentes de interface
│   ├── components.py           # Widgets reutilizáveis
│   └── filters.py              # Filtros da sidebar
│
├── tests/                      # 🆕 Testes unitários
│   ├── test_preprocessing.py
│   └── test_validators.py
│
├── .devcontainer/              # Configuração Codespaces
├── pyproject.toml              # Dependências Poetry
├── requirements.txt            # 🆕 Dependências pip
└── README.md
```

### 📐 Princípios de Design

- **Separação de responsabilidades**: UI, lógica e dados separados
- **Clean Code**: Funções pequenas, nomes descritivos
- **Error Handling**: Tratamento robusto em todas as camadas
- **Testabilidade**: Código fácil de testar
- **Performance**: Cache e otimizações

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.12 ou superior
- pip ou Poetry

### Opção 1: Com Poetry (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/edsondeveza/fiis_web.git
cd fiis_web

# Instale dependências
poetry install

# Ative o ambiente
poetry env activate
```

### Opção 2: Com pip

```bash
# Clone o repositório
git clone https://github.com/edsondeveza/fiis_web.git
cd fiis_web

# Crie ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

---

## 🖥 Como Executar

```bash
streamlit run app.py
```

O app abrirá automaticamente em `http://localhost:8501`

### Primeira Execução

Na primeira vez, o app irá:

1. Conectar ao Fundamentus (pode levar ~10s)
2. Processar e validar dados
3. Cachear para uso futuro

Execuções seguintes serão **instantâneas** (dados em cache por 1 hora).

---

## 🧪 Testes

Execute os testes unitários:

```bash
# Com pytest
pytest tests/ -v

# Com coverage
pytest tests/ --cov=core --cov-report=html
```

---

## 📊 Pipeline de Dados

```
┌─────────────────────┐
│  Fundamentus.com.br │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Data Loader  │  ← Retry automático
    │  + Validação │  ← Timeout handling
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Normalização │  ← Remove acentos
    │              │  ← Padroniza nomes
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Conversão   │  ← String → Float
    │   Numérica   │  ← Trata percentuais
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │Enriquecimento│  ← DY%, Vacância%
    │              │  ← Macro-segmentos
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Validação   │  ← Verifica colunas
    │    Final     │  ← Qualidade mínima
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    Cache     │  ← 1 hora TTL
    └──────────────┘
```

---

## ⚙️ Configuração

Edite `config.py` para ajustar:

```python
class Config:
    # Cache
    cache.ttl_seconds = 3600  # 1 hora
    
    # Timeout
    fundamentus.timeout = 30  # segundos
    
    # Filtros padrão
    filtros_iniciante.min_dy = 8.0
    filtros_iniciante.max_pvp = 1.20
    
    # UI
    ui.max_fiis_radar = 5
```

---

## 🔮 Roadmap

### Em Desenvolvimento

- [ ] Gráficos de histórico (DY, P/VP)
- [ ] Comparação com IFIX
- [ ] Exportação PDF com análise

### Futuro

- [ ] Deploy na nuvem (Railway/Streamlit Cloud)
- [ ] Dark mode
- [ ] API REST
- [ ] Backtesting de estratégias
- [ ] Alertas personalizados
- [ ] Integração com Status Invest

---

## 📚 Tecnologias

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| Python | 3.12+ | Linguagem base |
| Streamlit | 1.51+ | Interface web |
| Pandas | 2.3+ | Manipulação de dados |
| Plotly | 6.4+ | Gráficos interativos |
| Requests | 2.32+ | HTTP client |
| lxml | 6.0+ | Parse HTML |
| Poetry | 1.9+ | Gerenciamento de dependências |
| pytest | - | Testes unitários |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Guidelines

- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação
- Use commits semânticos

---

## 📝 Changelog

### v2.0.0 (2025-01-XX)

- 🎉 Refatoração completa da arquitetura
- ✨ Cache inteligente implementado
- 🛡️ Tratamento robusto de erros
- 🧪 Testes unitários adicionados
- 📦 Módulos UI separados
- ⚙️ Configurações centralizadas
- 📊 Validação de dados em múltiplas camadas
- 🎨 UX melhorada com sugestões inteligentes

### v1.0.0 (2024-12-XX)

- 🎉 Versão inicial
- 📊 Análise básica de FIIs
- 🔍 Sistema de filtros
- 🧬 Busca de semelhantes
- 🕸 Gráfico radar

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## ⚠️ Disclaimer

Esta ferramenta é destinada **exclusivamente para fins educacionais e de estudo**.

**NÃO é recomendação de investimento.**

Os dados são fornecidos pelo Fundamentus e podem conter imprecisões. Sempre faça sua própria análise e consulte um profissional certificado antes de investir.

O autor não se responsabiliza por decisões de investimento tomadas com base nesta ferramenta.

---

## 👨‍💻 Autor

**Edson Deveza**  
Analista de Suporte Técnico • Desenvolvedor Python 

📧 <edsondeveza@hotmail.com>  
🐙 [GitHub](https://github.com/edsondeveza)  
💼 [LinkedIn](https://linkedin.com/in/edsondeveza)  
📍 Brasil

---

## 🙏 Agradecimentos

- [Fundamentus](https://www.fundamentus.com.br) pelos dados
- [Streamlit](https://streamlit.io) pela excelente framework
- Comunidade Python brasileira

---

## ⭐ Se você gostou

Se este projeto foi útil, considere dar uma ⭐ no repositório!

---

**Desenvolvido com ❤️ e ☕ no Brasil**
