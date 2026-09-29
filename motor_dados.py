import yfinance as yf
import pandas as pd
import os

def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500):
    """
    LEITURA INTELIGENTE:
    - Se o ficheiro CSV já existe no cofre (gerado pelo robô), lê-o instantaneamente (para o Streamlit).
    - Se não existir, vai à internet com estratégia em cascata (para o robô atualizar).
    """
    ativo_limpo = str(ativo).replace('.SA', '').upper().strip()
    arquivo_csv = f"{ativo_limpo}.csv"
    
    # 1. TENTA LER DO COFRE LOCAL (Prioridade máxima para o Streamlit)
    if os.path.exists(arquivo_csv):
        try:
            df = pd.read_csv(arquivo_csv, index_col=0, parse_dates=True)
            if not df.empty:
                df.index = pd.to_datetime(df.index).tz_localize(None)
                df.columns = [str(c).capitalize() for c in df.columns]
                return df.tail(barras)
        except Exception:
            pass # Se houver qualquer falha na leitura local, tenta a internet como retaguarda

    # 2. PLANO DE RETAGUARDA / INTERNET (Usado pelo robô do GitHub)
    ativo_yf = f"{ativo_limpo}.SA"
    periodos_tentativa = ["2y", "max", "6mo", "1d"]
    
    df = None
    for p in periodos_tentativa:
        try:
            ticker = yf.Ticker(ativo_yf)
            df = ticker.history(period=p, interval=tempo_grafico)
            if df is not None and not df.empty:
                break
        except:
            continue
            
    if df is None or df.empty:
        return None
        
    try:
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.columns = [str(c).capitalize() for c in df.columns]
        return df.tail(barras)
    except Exception as e:
        print(f"Erro interno de formatação em {ativo_yf}: {e}")
        return None

# ==========================================
# ROTINA DE EXECUÇÃO AUTOMÁTICA DO ROBÔ
# ==========================================
if __name__ == "__main__":
    try:
        from config_ativos import bdrs_elite, ibrx_selecao, etfs_master
        
        lista_etfs = []
        for categoria, etfs in etfs_master.items():
            for ticker in etfs.keys():
                lista_etfs.append(f"{ticker}.SA")
                
        ativos_alvo = bdrs_elite + ibrx_selecao + lista_etfs
    except Exception as e:
        print(f"Aviso: Não encontrou config_ativos.py. Erro: {e}")
        ativos_alvo = ['PETR4.SA', 'VALE3.SA'] 

    ativos = list(set([a.replace('.SA', '') for a in ativos_alvo]))

    print(f"Iniciando atualização de {len(ativos)} ativos no cofre...")

    for ativo in ativos:
        try:
            # Aqui forçamos a busca externa para atualizar o CSV no GitHub
            ativo_yf = f"{ativo}.SA"
            df = None
            for p in ["2y", "max", "6mo", "1d"]:
                try:
                    df = yf.Ticker(ativo_yf).history(period=p, interval="1d")
                    if df is not None and not df.empty:
                        break
                except:
                    continue
            
            if df is not None and not df.empty:
                df.index = pd.to_datetime(df.index).tz_localize(None)
                df.columns = [str(c).capitalize() for c in df.columns]
                df.to_csv(f"{ativo}.csv")
                print(f"✅ {ativo}.csv guardado com sucesso!")
            else:
                print(f"⚠️ Sem dados na Bolsa para {ativo}.")
        except Exception as e:
            print(f"❌ Erro fatal ao salvar {ativo}: {e}")
            
    print("Todas as operações concluídas com sucesso! Cofre atualizado.")
