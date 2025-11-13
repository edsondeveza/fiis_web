# 📊 FIIs Web — Análise Inteligente de Fundos Imobiliários (Python + Streamlit)

Uma aplicação web interativa para análise completa de **Fundos Imobiliários (FIIs)** a partir dos dados públicos do **Fundamentus**, com filtros dinâmicos, dashboards, comparação visual entre fundos e busca avançada por fundos semelhantes.

Construído com **Python 3.12**, **Streamlit**, **Pandas** e **Plotly**.

---

## 📌 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Pipeline de Dados](#-pipeline-de-dados)
- [Instalação](#-instalação)
- [Como Executar](#-como-executar)
- [Capturas de Tela](#-capturas-de-tela)
- [Roadmap](#-roadmap)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Autor](#-autor)

---

## 📌 Sobre o Projeto

Este projeto nasceu da necessidade de analisar FIIs de forma simples, organizada e **totalmente automatizada**, sem depender de copiar/colar dados do site do Fundamentus.

A aplicação:

✔ Baixa automaticamente os dados mais recentes dos FIIs  
✔ Realiza todo o tratamento, normalização e enriquecimento das informações  
✔ Aplica regras configuráveis para filtrar fundos  
✔ Calcula *score* de qualidade de 0 a 5  
✔ Permite exportar resultados em Excel/CSV  
✔ Compara fundos com gráficos **radar interativos**  
✔ Traz sistema inteligente para buscar FIIs semelhantes ao fundo escolhido

É uma ferramenta de **estudo** e não uma recomendação de investimento.

---

## ✨ Funcionalidades

### 🔎 Carregamento de Dados

- Coleta automática dos dados do Fundamentus (web scraping)
- Pipeline completo de limpeza e padronização
- Correção de percentuais (DY, vacância, FFO, cap rate etc.)

### 🎚 Modo Iniciante e Modo Avançado

- **Iniciante** → parâmetros pré-definidos e explicados
- **Avançado** → liberdade total nos filtros (DY, P/VP, liquidez, vacância, valor de mercado)

### 📊 Filtros personalizáveis

- DY mínimo
- P/VP máximo
- Liquidez mínima
- Vacância máxima
- Valor de mercado mínimo
- Score mínimo (0–5)
- Macro-segmento
- Segmento específico

### 🧮 Cálculo de Score (0 a 5)

Critérios avaliados:

1. DY bom  
2. P/VP bom  
3. Liquidez mínima  
4. Vacância controlada  
5. Tamanho do fundo (market cap)

### 📈 Dashboard interativo

- DY médio do mercado
- P/VP médio
- Vacância média
- Valor total de mercado dos FIIs
- Total de FIIs carregados

### 🧬 Busca de FIIs semelhantes

Sistema inteligente que sugere:

- Tolerância de DY
- Tolerância de P/VP
- Liquidez mínima

Baseado no fundo alvo e seu segmento.

### 🕸 Gráfico Radar

Comparação visual entre:

- DY
- P/VP
- Liquidez
- Vacância
- Valor de mercado
- Score

### 💾 Exportação

- Exportar filtros em **CSV**
- Exportar em **Excel (.xlsx)**
- Exportar fundos semelhantes

---

## 🏗 Arquitetura do Projeto

```text
fiis_web/
│
├── app.py                 # Interface Streamlit (frontend)
│
├── core/
│   ├── data_loader.py     # Coleta online do Fundamentus
│   ├── preprocessing.py   # Normalização + limpeza + percentuais
│   ├── scoring.py         # Aplicação das regras e score
│   ├── similarity.py      # Algoritmo de fundos semelhantes
│   ├── utils.py           # Funções auxiliares (ordenar etc.)
│
├── README.md
└── pyproject.toml         # Projeto Poetry
```

Cada módulo tem responsabilidade única seguindo boas práticas de Clean Code.

---

## 🧠 Pipeline de Dados

1. **Coleta:**  
   - HTML do Fundamentus é baixado e convertido em tabela

2. **Normalização:**  
   - Remove acentos  
   - Ajusta nomes de colunas  
   - Padroniza formatos

3. **Tratamento Numérico:**  
   - Converte strings para float/int  
   - Remove símbolos e percentuais  
   - Trata números no formato brasileiro (“3,25%”)

4. **Enriquecimento:**  
   - Cria DY%, FFO%, vacância%  
   - Classifica em macro-segmentos

5. **Aplicação de Regras:**  
   - DY mínimo  
   - P/VP máximo  
   - Liquidez mínima  
   - Vacância máxima  
   - Valor de mercado mínimo

6. **Score:**  
   - Soma das flags (0–5)

7. **Exibição e exportação no Streamlit**

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/fiis_web.git
cd fiis_web
```

### 2. Instale as dependências com Poetry

```bash
poetry install
```

> O projeto exige **Python 3.12+**

### 3. Ative o ambiente virtual

```bash
poetry shell
```

---

## 🖥 Como Executar

```bash
streamlit run app.py
```

Após alguns segundos, a aplicação abrirá no navegador:

```text
http://localhost:8501
```

---

## 📸 Capturas de Tela

> *Adicione prints reais do seu app depois.*

### Dashboard inicial  

*(placeholder)*  
![dashboard](docs/dashboard.png)

### Tabela filtrada  

*(placeholder)*  
![tabela](docs/fiis_table.png)

### Radar Chart  

*(placeholder)*  
![radar](docs/radar_chart.png)

---

## 🔮 Roadmap

- [ ] Histórico real de DY e P/VP via API externa  
- [ ] Comparação de carteiras (FII x FII x IFIX)  
- [ ] Backtesting básico  
- [ ] Exportação em PDF  
- [ ] Dark mode  
- [ ] Deploy na nuvem (Railway / Streamlit Cloud / HuggingFace Spaces)  
- [ ] Cache inteligente para reduzir chamadas ao Fundamentus  
- [ ] IA para sugerir ajustes nos filtros  

---

## 📚 Tecnologias Utilizadas

- **Python 3.12**
- **Streamlit**
- **Pandas**
- **Plotly**
- **Requests**
- **lxml**
- **OpenPyXL**
- **Poetry**
- (Opcional) BeautifulSoup / html5lib

---

## 👨‍💻 Autor

**Edson Deveza**  
Analista de Suporte Técnico • Desenvolvedor Python • Pastor  
📧 <edsondeveza@hotmail.com>  
📍 Brasil  
