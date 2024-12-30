from PIL import Image
import pandas as pd
import streamlit as st
import yfinance as yf

# Carregando Logomarca
image = Image.open("IMAGE.png")

# Abrindo logomarca no Streamlit
col1, col2, col3 = st.columns(3)

# with col1:
#     st.write("")

with col2:
    st.image(image, width=700, use_column_width=False)

# with col3:
#     st.write("")

# Iniciando APP
st.markdown("<h1 style='text-align: center; color: red;'>ALOCAÇÃO DE ATIVOS</h1>", unsafe_allow_html=True)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

CAPITAL = st.number_input('Digite o valor de seu aporte')

def Main():
    # Baixando dados históricos de IVVB11, GOLD11 e BOVA11
    IVVB11 = yf.download("IVVB11.SA", period="10y")
    GOLD = yf.download("GOLD11.SA", period="10y")
    BOVESPA = yf.download("BOVA11.SA", period="10y")

    # Verificando se os DataFrames não estão vazios e contêm a coluna 'Close'
    if not IVVB11.empty and 'Close' in IVVB11.columns:
        PRECO_IVVB11 = IVVB11["Close"].iloc[-1]
        IVVB11_HIGH = IVVB11['High'].max()
    else:
        PRECO_IVVB11 = None
        IVVB11_HIGH = None
        st.warning("Dados do IVVB11 não disponíveis.")

    if not GOLD.empty and 'Close' in GOLD.columns:
        PRECO_GOLD = GOLD["Close"].iloc[-1]
        GOLD_HIGH = GOLD['High'].max()
    else:
        PRECO_GOLD = None
        GOLD_HIGH = None
        st.warning("Dados do GOLD11 não disponíveis.")

    if not BOVESPA.empty and 'Close' in BOVESPA.columns:
        PRECO_BOVESPA = BOVESPA["Close"].iloc[-1]
        BOVESPA_HIGH = BOVESPA['High'].max()
    else:
        PRECO_BOVESPA = None
        BOVESPA_HIGH = None
        st.warning("Dados do BOVA11 não disponíveis.")

    # Baixando dados do último dia para GOLD11 e BOVA11
    GOLD11 = yf.download("GOLD11.SA", period="1d")
    BOVA11 = yf.download("BOVA11.SA", period="1d")

    # Criando DataFrame com os dados de alocação
    COLUNAS = ["Topo Historico", "Cotação Atual", "Relativo", "Ajustado", "Percentual"]
    DADOS = pd.DataFrame(columns=COLUNAS)
    DADOS["Topo Historico"] = [BOVESPA_HIGH, IVVB11_HIGH, GOLD_HIGH]
    DADOS.index = ["IBOV", "IVVB11", "GOLD"]
    DADOS['Cotação Atual'] = [PRECO_BOVESPA, PRECO_IVVB11, PRECO_GOLD]
    
    FATOR = 0.60 * DADOS["Topo Historico"]
    AMPLITUDE = DADOS["Topo Historico"] - DADOS['Cotação Atual']
    DADOS['Relativo'] = AMPLITUDE / FATOR
    DADOS.iloc[2, 2] = 2 * DADOS.iloc[2, 2]  # Ajuste específico para GOLD

    SOMA = DADOS['Relativo'].sum()
    DADOS['Ajustado'] = 100 * (DADOS['Relativo'] / SOMA)
    DADOS['Percentual'] = (25.00 + DADOS['Ajustado'] / 4.00) / 100.00
    DADOS['Valor por ativo'] = CAPITAL * DADOS['Percentual']
    
    return DADOS

if CAPITAL:
    resultado = Main()
    if resultado is not None:
        st.write("Tabela de Alocação de ativos")
        st.dataframe(resultado)
