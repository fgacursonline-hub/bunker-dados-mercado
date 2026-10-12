import yfinance as yf
import pandas as pd
import os

def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500):
    """
    LEITURA INTELIGENTE MATEMÁTICA:
    - Lê o CSV Diário local. Se o painel pedir Semanal/Mensal, funde os dias matematicamente na unha.
    """
    ativo_limpo = str(ativo).replace('.SA', '').upper().strip()
    arquivo_csv = f"{ativo_limpo}.csv"
    
    # 1. TENTA LER DO COFRE LOCAL E CONVERTER TEMPOS GRÁFICOS
    if os.path.exists(arquivo_csv):
        try:
            df = pd.read_csv(arquivo_csv, index_col=0, parse_dates=True)
            if not df.empty:
                df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
                df.columns = [str(c).strip().capitalize() for c in df.columns]
                
                # MOTOR QUANTITATIVO BLINDADO: Agrupa dias matematicamente sem usar 'resample'
                agg_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}
                
                if tempo_grafico == "1wk":
                    # Agrupa por Ano e Semana do Ano
                    df['Group'] = df.index.strftime('%Y-%W')
                    df_grouped = df.groupby('Group').agg(agg_dict)
                    df_grouped.index = df.groupby('Group').apply(lambda x: x.index.max()).values
                    df = df_grouped.sort_index()
                    
                elif tempo_grafico == "1mo":
                    # Agrupa por Ano e Mês
                    df['Group'] = df.index.strftime('%Y-%m')
                    df_grouped = df.groupby('Group').agg(agg_dict)
                    # A data de cada vela mensal será o último dia do mês encontrado na base
                    df_grouped.index = df.groupby('Group').apply(lambda x: x.index.max()).values
                    df = df_grouped.sort_index()
                    
                return df.tail(barras)
        except Exception as e:
            print(f"Aviso: Falha na conversão local de {ativo} -> {e}")

    # 2. PLANO DE RETAGUARDA / INTERNET (Yahoo Finance)
    ativo_yf = f"{ativo_limpo}.SA"
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
        df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df.tail(barras)
    except Exception:
        return None

# ==========================================
# ROTINA DE EXECUÇÃO AUTOMÁTICA DO ROBÔ
# ==========================================
if __name__ == "__main__":
    try:
        from config_ativos import bdrs_elite, ibrx_selecao
        ativos_alvo = bdrs_elite + ibrx_selecao
    except Exception:
        ativos_alvo = ['PETR4.SA', 'VALE3.SA'] 

    ativos = list(set([a.replace('.SA', '') for a in ativos_alvo]))
    print(f"Iniciando atualização de {len(ativos)} ativos no cofre com histórico MÁXIMO...")

    for ativo in ativos:
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
