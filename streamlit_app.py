from PIL import Image
import pandas as pd
import streamlit as st
import yfinance as yf

# Carregando Logomarca
image = Image.open("IMAGE.png")
# Abrindo logomarca no Streamlit
col1, col2, col3 = st.columns(3)

# Exibindo a imagem no centro da tela
st.image(image, width=700, use_column_width=False)

# Iniciando APP
st.markdown("<h1 style='text-align: center; color: red;'>ALOCAÇÃO DE ATIVOS</h1>", unsafe_allow_html=True)

# Escondendo o menu do Streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Entrada do valor de aporte
CAPITAL = st.number_input('Digite o valor de seu aporte')

# Função principal de alocação
def Main():
    try:
        # Baixando dados históricos de IVVB11, GOLD e BOVESPA
        IVVB11 = yf.download("IVVB11.SA", period="10y")
        PRECO_IVVB11 = IVVB11["Close"].iloc[-1]
        IVVB11_HIGH = IVVB11['High'].max()
        
        GOLD = yf.download("GOLD11.SA", period="10y")
        PRECO_GOLD = GOLD["Close"].iloc[-1]
        GOLD_HIGH = GOLD['High'].max()
        
        BOVESPA = yf.download("BOVA11.SA", period="10y")
        PRECO_BOVESPA = BOVESPA["Close"].iloc[-1]
        BOVESPA_HIGH = BOVESPA['High'].max()

        # Baixando dados do dia atual (1 dia) para GOLD11 e BOVA11
        GOLD11 = yf.download("GOLD11.SA", period="1d")
        BOVA11 = yf.download("BOVA11.SA", period="1d")

        # Definindo as colunas para o DataFrame de alocação
        COLUNAS = ["Topo Historico", "Cotação Atual", "Relativo", "Ajustado", "Percentual", "Valor por ativo"]
        DADOS = pd.DataFrame(columns=COLUNAS)

        # Preenchendo os dados de histórico e preços atuais
        DADOS["Topo Historico"] = [BOVESPA_HIGH, IVVB11_HIGH, GOLD_HIGH]
        DADOS.index = ["IBOV", "IVVB11", "GOLD"]
        DADOS['Cotação Atual'] = [PRECO_BOVESPA, PRECO_IVVB11, PRECO_GOLD]

        # Calculando o fator e a amplitude
        FATOR = 0.60 * DADOS["Topo Historico"]
        AMPLITUDE = DADOS["Topo Historico"] - DADOS['Cotação Atual']

        # Calculando o relativo e ajustando o valor de GOLD
        DADOS['Relativo'] = AMPLITUDE / FATOR
        DADOS.iloc[2, 2] = 2 * DADOS.iloc[2, 2]  # Ajuste para GOLD

        # Calculando a soma dos relativos e ajustando os percentuais
        SOMA = DADOS['Relativo'].sum()
        DADOS['Ajustado'] = 100 * (DADOS['Relativo'] / SOMA)
        DADOS['Percentual'] = (25.00 + DADOS['Ajustado'] / 4.00) / 100.00

        # Calculando o valor por ativo com base no aporte
        DADOS['Valor por ativo'] = CAPITAL * DADOS['Percentual']

        return DADOS

    except Exception as e:
        st.error(f"Erro ao baixar dados financeiros: {e}")
        return pd.DataFrame(columns=["Topo Historico", "Cotação Atual", "Relativo", "Ajustado", "Percentual", "Valor por ativo"])

# Verificando se o valor de CAPITAL foi inserido
if CAPITAL:
    resultado = Main()
    
    if not resultado.empty:
        st.write("Tabela de Alocação de Ativos")
        st.dataframe(resultado)
    else:
        st.warning("Não foi possível gerar os dados de alocação de ativos.")
