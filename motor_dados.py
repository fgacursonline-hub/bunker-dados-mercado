import os
import warnings
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")

# Pega o diretório exato onde o motor_dados.py está salvo
DIRETORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
# Trava o caminho do Bunker na raiz do projeto
PASTA_BUNKER = os.path.join(DIRETORIO_RAIZ, "bunker_dados")

def _normalizar_ativo(ativo):
    """Limpa o nome do ativo para bater com o arquivo salvo pelo GitHub."""
    ativo = "" if ativo is None else str(ativo)
    ativo = ativo.upper().strip().replace(".SA", "")
    return ativo

def _padronizar_dataframe(df):
    """Garante colunas e tipos padronizados."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    
    # Se veio algum MultiIndex residual, remove
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # Padroniza as colunas com a primeira letra maiúscula
    df.columns = [str(c).capitalize() for c in df.columns]

    colunas_obrigatorias = ["Open", "High", "Low", "Close"]
    
    # Se faltar coluna essencial, aborta
    if any(c not in df.columns for c in colunas_obrigatorias):
        return pd.DataFrame()

    # Força ser numérico
    for col in colunas_obrigatorias:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Limpa dados corrompidos
    df = df.dropna(subset=colunas_obrigatorias)
    df = df[~df.index.duplicated(keep="last")]

    # Remove timezone do index para evitar conflitos no Streamlit/Plotly
    try:
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_localize(None)
    except Exception:
        pass

    return df

@st.cache_data(ttl=300, show_spinner=False) 
def _ler_do_bunker(ativo_limpo, tempo_grafico, barras):
    """Lê diretamente do disco (Parquet) e joga na RAM do Streamlit por 5 minutos."""
    caminho_arquivo = os.path.join(PASTA_BUNKER, f"{ativo_limpo}_{tempo_grafico}.parquet")
    
    if not os.path.exists(caminho_arquivo):
        return pd.DataFrame()
        
    try:
        df = pd.read_parquet(caminho_arquivo)
        df = _padronizar_dataframe(df)
        return df.tail(barras)
    except Exception:
        return pd.DataFrame()

def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=150):
    """
    Função pública usada pelas páginas Streamlit.
    Agora é 100% passiva e blindada: apenas lê os dados que o robô do GitHub atualiza.
    """
    ativo_limpo = _normalizar_ativo(ativo)
    barras_int = int(barras)
    
    return _ler_do_bunker(ativo_limpo, str(tempo_grafico), barras_int)
