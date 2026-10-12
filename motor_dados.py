import yfinance as yf
import pandas as pd
import os

def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500):
    """
    LEITURA INTELIGENTE COM RESAMPLING:
    - Lê o CSV Diário local. Se o painel pedir Semanal/Mensal, funde os dias matematicamente.
    - Se pedir Intraday, ignora o CSV e vai à net buscar os dados com as limitações corretas.
    """
    ativo_limpo = str(ativo).replace('.SA', '').upper().strip()
    arquivo_csv = f"{ativo_limpo}.csv"
    
    # 1. TENTA LER DO COFRE LOCAL E CONVERTER TEMPOS GRÁFICOS
    if os.path.exists(arquivo_csv):
        try:
            df = pd.read_csv(arquivo_csv, index_col=0, parse_dates=True)
            if not df.empty:
                df.index = pd.to_datetime(df.index).tz_localize(None)
                df.columns = [str(c).capitalize() for c in df.columns]
                
                # MOTOR QUANTITATIVO: Agrupa dias para formar Semanas ou Meses
                if tempo_grafico == "1wk":
                    df = df.resample('W').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
                elif tempo_grafico == "1mo":
                    # Tenta a regra do Pandas moderno ('ME'), se falhar usa a regra clássica ('M')
                    try:
                        df = df.resample('ME').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
                    except:
                        df = df.resample('M').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
                elif tempo_grafico in ["15m", "60m"]:
                    # Intraday não existe no CSV, força a ir à internet buscar dados frescos
                    raise ValueError("Pular para Plano B")
                    
                return df.tail(barras)
        except Exception:
            pass # Se falhar a montagem do mensal/semanal, passa para a internet

    # 2. PLANO DE RETAGUARDA / INTERNET (Yahoo Finance)
    ativo_yf = f"{ativo_limpo}.SA"
    
    # AJUSTE INTELIGENTE DE PERÍODO: Impede que a API bloqueie os pedidos Intraday
    if tempo_grafico == "15m":
        periodos_tentativa = ["60d", "1mo", "5d"]
    elif tempo_grafico == "60m":
        periodos_tentativa = ["730d", "1y", "6mo"]
    else:
        periodos_tentativa = ["max", "10y", "5y", "2y"]
        
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

    print(f"Iniciando atualização de {len(ativos)} ativos no cofre com histórico MÁXIMO...")

    for ativo in ativos:
        try:
            ativo_yf = f"{ativo}.SA"
            df = None
            
            # Baixa sempre em Diário e com histórico Máximo para montar o Bunker forte
            for p in ["max", "10y", "5y", "2y"]:
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
            
    print("Todas as operações concluídas com sucesso! Cofre atualizado com histórico profundo.")
