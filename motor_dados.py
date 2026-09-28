import yfinance as yf
import pandas as pd
import os

def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500):
    """Função com estratégia em cascata para garantir que nenhum ativo falhe."""
    ativo_limpo = ativo.replace('.SA', '')
    ativo_yf = f"{ativo_limpo}.SA"
    
    # Lista de tentativas de períodos do menor para o maior (ou vice-versa)
    periodos_tentativa = ["2y", "max", "6mo", "1d"]
    
    df = None
    for p in periodos_tentativa:
        try:
            ticker = yf.Ticker(ativo_yf)
            df = ticker.history(period=p, interval=tempo_grafico)
            if df is not None and not df.empty:
                break # Conseguiu baixar, sai do loop!
        except:
            continue
            
    if df is None or df.empty:
        return None
        
    try:
        # Remove o fuso horário para evitar problemas de compatibilidade
        df.index = pd.to_datetime(df.index).tz_localize(None)
        
        # Formata as colunas
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
        
        # Extrair os tickers dos ETFs do dicionário etfs_master
        lista_etfs = []
        for categoria, etfs in etfs_master.items():
            for ticker in etfs.keys():
                lista_etfs.append(f"{ticker}.SA")
                
        ativos_alvo = bdrs_elite + ibrx_selecao + lista_etfs
    except Exception as e:
        print(f"Aviso: Não encontrou config_ativos.py. Erro: {e}")
        ativos_alvo = ['PETR4.SA', 'VALE3.SA'] 

    # Remove duplicados e padroniza os nomes
    ativos = list(set([a.replace('.SA', '') for a in ativos_alvo]))

    print(f"Iniciando download de {len(ativos)} ativos diretamente da Bolsa (incluindo ETFs)...")

    for ativo in ativos:
        try:
            df = puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500)
            
            if df is not None and not df.empty:
                # Salva o arquivo CSV físico no repositório
                df.to_csv(f"{ativo}.csv")
                print(f"✅ {ativo}.csv guardado com sucesso!")
            else:
                print(f"⚠️ Sem dados na Bolsa para {ativo}.")
        except Exception as e:
            print(f"❌ Erro fatal ao salvar {ativo}: {e}")
            
    print("Todas as operações concluídas com sucesso! Cofre atualizado.")
