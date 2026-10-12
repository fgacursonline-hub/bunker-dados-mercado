import yfinance as yf
import pandas as pd
import os

def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500):
    """
    LEITURA INTELIGENTE MATEMÁTICA:
    - Lê o CSV local. Se for Semanal/Mensal, funde dias matematicamente.
    - Se for Futuro (WIN/WDO) no intraday, lê do CSV local (ProfitChart/MT5).
    """
    ativo_limpo = str(ativo).replace('.SA', '').upper().strip()
    arquivo_csv = f"{ativo_limpo}.csv"
    
    # 1. TENTA LER DO COFRE LOCAL E CONVERTER TEMPOS GRÁFICOS
    if os.path.exists(arquivo_csv):
        try:
            # Proteção dupla: lê CSVs padrão (vírgula) ou nacionais do Profit (ponto e vírgula)
            df = pd.read_csv(arquivo_csv, index_col=0, parse_dates=True)
            if len(df.columns) < 3:
                df = pd.read_csv(arquivo_csv, index_col=0, parse_dates=True, sep=';', decimal=',')
                
            if not df.empty:
                df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
                df.columns = [str(c).strip().capitalize() for c in df.columns]
                
                agg_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}
                
                if tempo_grafico == "1wk":
                    df['Group'] = df.index.strftime('%Y-%W')
                    df_grouped = df.groupby('Group').agg(agg_dict)
                    df_grouped.index = df.groupby('Group').apply(lambda x: x.index.max()).values
                    df = df_grouped.sort_index()
                    
                elif tempo_grafico == "1mo":
                    df['Group'] = df.index.strftime('%Y-%m')
                    df_grouped = df.groupby('Group').agg(agg_dict)
                    df_grouped.index = df.groupby('Group').apply(lambda x: x.index.max()).values
                    df = df_grouped.sort_index()
                    
                elif tempo_grafico in ["15m", "60m"]:
                    # Se for Futuro, permite ler o CSV que o comandante baixou do Profit
                    if "WIN" in ativo_limpo or "WDO" in ativo_limpo:
                        pass 
                    else:
                        raise ValueError("Pular para a internet no intraday de ações")
                    
                return df.tail(barras)
        except Exception as e:
            print(f"Aviso: Falha na conversão local de {ativo} -> {e}")

    # 2. PLANO DE RETAGUARDA / INTERNET (Yahoo Finance)
    # O Yahoo Finance NÃO tem WIN1! nem WDO1!. Se for futuro e não tiver CSV local, aborta imediatamente.
    if "WIN" in ativo_limpo or "WDO" in ativo_limpo:
        return None
        
    ativo_yf = f"{ativo_limpo}.SA"
    
    if tempo_grafico == "15m": periodos_tentativa = ["60d", "1mo"]
    elif tempo_grafico == "60m": periodos_tentativa = ["730d", "1y"]
    else: periodos_tentativa = ["max", "10y", "5y", "2y"]
        
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
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df.tail(barras)
    except Exception:
        return None

# ============================================================
# ROTINA DE EXECUÇÃO AUTOMÁTICA DO ROBÔ
# ============================================================
if __name__ == "__main__":
    try:
        from config_ativos import bdrs_elite, ibrx_selecao
        ativos_alvo = bdrs_elite + ibrx_selecao
    except Exception:
        ativos_alvo = ['PETR4.SA', 'VALE3.SA'] 

    ativos = list(set([a.replace('.SA', '') for a in ativos_alvo]))
    print(f"Iniciando atualização de {len(ativos)} ativos no cofre com histórico MÁXIMO...")

    for ativo in ativos:
        if "WIN" in ativo or "WDO" in ativo:
            continue # Futuros não vêm da internet, vêm da extração manual do utilizador
            
        try:
            ativo_yf = f"{ativo}.SA"
            df = None
            
            for p in ["max", "10y", "5y", "2y"]:
                try:
                    df = yf.Ticker(ativo_yf).history(period=p, interval="1d")
                    if df is not None and not df.empty:
                        break
                except:
                    continue
            
            if df is not None and not df.empty:
                df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
                df.columns = [str(c).strip().capitalize() for c in df.columns]
                df.to_csv(f"{ativo}.csv")
                print(f"✅ {ativo}.csv guardado com sucesso!")
            else:
                print(f"⚠️ Sem dados na Bolsa para {ativo}.")
        except Exception as e:
            print(f"❌ Erro fatal ao salvar {ativo}: {e}")
            
    print("Cofre atualizado com sucesso!")
