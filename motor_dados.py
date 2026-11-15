import pandas as pd
import os
import streamlit as st

# NOTA: O yfinance FOI TOTALMENTE REMOVIDO DAQUI. O Streamlit não tem como ser banido.

@st.cache_data(ttl=900, max_entries=500, show_spinner=False)
def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500):
    ativo_limpo = str(ativo).replace('.SA', '').upper().strip()
    arquivo_csv = f"{ativo_limpo}.csv"
    
    # 1. LÊ EXCLUSIVAMENTE DO COFRE LOCAL
    if not os.path.exists(arquivo_csv):
        # AQUI ESTÁ A BLINDAGEM DEFINITIVA: 
        # Se o CSV não existe, ele desiste. Ele NUNCA tenta ir na internet buscar.
        return None
        
    try:
        df = pd.read_csv(arquivo_csv, index_col=0, parse_dates=True)
        if len(df.columns) < 3:
            df = pd.read_csv(arquivo_csv, index_col=0, parse_dates=True, sep=';', decimal=',')
            
        if df.empty:
            return None
            
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        
        # Agrupamento matemático das velas...
        agg_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}
        
        if tempo_grafico == "1wk":
            df['Group'] = df.index.strftime('%Y-%W')
            df = df.groupby('Group').agg(agg_dict)
            df.index = df.index.map(lambda x: pd.to_datetime(x + '-0', format='%Y-%W-%w'))
            
        elif tempo_grafico == "1mo":
            df['Group'] = df.index.strftime('%Y-%m')
            df = df.groupby('Group').agg(agg_dict)
            df.index = pd.to_datetime(df.index)
            
        return df.tail(barras)
        
    except Exception as e:
        print(f"Erro ao ler cofre local para {ativo}: {e}")
        return None
