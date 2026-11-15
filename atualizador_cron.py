# atualizador_cron.py - NUNCA É CHAMADO PELO STREAMLIT
import yfinance as yf
import pandas as pd
from config_ativos import bdrs_elite, ibrx_selecao
import time

def atualizar_bunker():
    ativos_alvo = bdrs_elite + ibrx_selecao
    ativos = list(set([a.replace('.SA', '') for a in ativos_alvo]))
    
    print(f"Iniciando atualização em lote offline de {len(ativos)} ativos...")

    for ativo in ativos:
        if "WIN" in ativo or "WDO" in ativo:
            continue # Futuros você sobe o CSV manualmente via Profit
            
        try:
            df = yf.Ticker(f"{ativo}.SA").history(period="5y", interval="1d")
            if df is not None and not df.empty:
                df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
                df.columns = [str(c).strip().capitalize() for c in df.columns]
                df.to_csv(f"{ativo}.csv")
                print(f"✅ Atualizado: {ativo}.csv")
            
            time.sleep(1) # Pausa amigável de 1 segundo para não estressar a API
        except Exception as e:
            print(f"❌ Erro ao baixar {ativo}: {e}")

if __name__ == "__main__":
    atualizar_bunker()
