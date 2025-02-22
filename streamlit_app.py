import time
import yfinance as yf
import pandas as pd
import streamlit as st

# Função para tentar baixar dados com retries em caso de erro
def fetch_data(ticker, period="1y", retries=3, delay=5):
    """
    Função para baixar dados com retry em caso de erro.
    """
    attempt = 0
    while attempt < retries:
        try:
            data = yf.download(ticker, period=period)
            if data.empty:
                raise ValueError("Dados vazios")
            return data
        except Exception as e:
            attempt += 1
            st.warning(f"Tentativa {attempt} falhou para {ticker}. Erro: {e}")
            if attempt < retries:
                st.warning(f"Aguardando {delay} segundos antes de tentar novamente...")
                time.sleep(delay)  # Espera entre tentativas
            else:
                st.error(f"Falha ao carregar dados de {ticker} após {retries} tentativas.")
                return None
    return None

# Função principal do aplicativo
def Main(CAPITAL):
    # Baixando dados dos ativos
    IVVB11 = fetch_data("IVVB11.SA", period="10y")
    if IVVB11 is None:
        return None
    PRECO_IVVB11 = IVVB11["Close"].iloc[-1] if not IVVB11["Close"].empty else 0
    IVVB11_HIGH = IVVB11['High'].max() if not IVVB11['High'].empty else 0

    GOLD = fetch_data("GOLD11.SA", period="4y")
    if GOLD is None:
        return None
    PRECO_GOLD = GOLD["Close"].iloc[-1] if not GOLD["Close"].empty else 0
    GOLD_HIGH = GOLD['High'].max() if not GOLD['High'].empty else 0

    BOVESPA = fetch_data("BOVA11.SA", period="10y")
    if BOVESPA is None:
        return None
    PRECO_BOVESPA = BOVESPA["Close"].iloc[-1] if not BOVESPA["Close"].empty else 0
    BOVESPA_HIGH = BOVESPA['High'].max() if not BOVESPA['High'].empty else 0

    # Criando DataFrame para armazenar os dados
    COLUNAS = ["Topo Historico", "Cotação Atual", "Relativo", "Ajustado", "Percentual"]
    DADOS = pd.DataFrame(columns=COLUNAS)
    
    DADOS["Topo Historico"] = [BOVESPA_HIGH, IVVB11_HIGH, GOLD_HIGH]
    DADOS.index = ["IBOV", "IVVB11", "GOLD"]
    DADOS['Cotação Atual'] = [PRECO_BOVESPA, PRECO_IVVB11, PRECO_GOLD]
    
    # Calculando o fator e a amplitude
    FATOR = 0.60 * DADOS["Topo Historico"]
    AMPLITUDE = DADOS["Topo Historico"] - DADOS['Cotação Atual']
    DADOS['Relativo'] = AMPLITUDE / FATOR
    DADOS.iloc[2, 2] = 2 * DADOS.iloc[2, 2]  # Ajuste específico para GOLD
    SOMA = DADOS['Relativo'].sum()
    
    # Calculando o valor ajustado e percentual
    DADOS['Ajustado'] = 100 * (DADOS['Relativo'] / SOMA)
    DADOS['Percentual'] = (25.00 + DADOS['Ajustado'] / 4.00) / 100.00
    DADOS['Valor por ativo'] = CAPITAL * DADOS['Percentual']
    
    return DADOS

# Código de interface do usuário com Streamlit
st.markdown("<h1 style='text-align: center; color: red;'>ALOCAÇÃO DE ATIVOS</h1>", unsafe_allow_html=True)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Capturando o valor do capital do usuário
CAPITAL = st.number_input('Digite o valor de seu aporte')

if CAPITAL > 0:
    resultado = Main(CAPITAL)
    if resultado is not None:
        st.write("Tabela de Alocação de ativos")
        st.dataframe(resultado)
