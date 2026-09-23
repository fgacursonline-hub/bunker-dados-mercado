import yfinance as yf
import pandas as pd
import os

def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500):
    """Função pura que vai à internet (Yahoo Finance) puxar os dados reais."""
    ativo_limpo = ativo.replace('.SA', '')
    ativo_yf = f"{ativo_limpo}.SA"
    
    try:
        ticker = yf.Ticker(ativo_yf)
        # Puxa o histórico máximo disponível
        df = ticker.history(period="max", interval=tempo_grafico)
        
        if df.empty:
            return None
            
        # Remove o fuso horário para evitar problemas de compatibilidade
        df.index = pd.to_datetime(df.index).tz_localize(None)
        
        # Formata as colunas
        df.columns = [str(c).capitalize() for c in df.columns]
        
        return df.tail(barras)
    except Exception as e:
        print(f"Erro interno YFinance em {ativo_yf}: {e}")
        return None

# ==========================================
# ROTINA DE EXECUÇÃO AUTOMÁTICA DO ROBÔ
# ==========================================
if __name__ == "__main__":
    try:
        from config_ativos import bdrs_elite, ibrx_selecao
        ativos_alvo = bdrs_elite + ibrx_selecao
    except Exception as e:
        print(f"Aviso: Não encontrou config_ativos.py. Erro: {e}")
        ativos_alvo = ['PETR4.SA', 'VALE3.SA'] 

    # Remove duplicados e padroniza os nomes
    ativos = list(set([a.replace('.SA', '') for a in ativos_alvo]))

    print(f"Iniciando download de {len(ativos)} ativos diretamente da Bolsa...")

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
