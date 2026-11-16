import pandas as pd
import yfinance as yf
from tvDatafeed import TvDatafeed, Interval
import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime, timedelta
import os
import sys

try:
    from config_ativos import bdrs_elite, ibrx_selecao, bdr_setup_home, etfs_master
except ImportError:
    print("Aviso: config_ativos.py não encontrado.")
    bdrs_elite, ibrx_selecao, bdr_setup_home, etfs_master = [], [], {}, {}

# Controle de falhas
ERROS_REGISTRADOS = 0

def registrar_log(mensagem, erro=False):
    global ERROS_REGISTRADOS
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    prefixo = "❌ ERRO:" if erro else "✅"
    if erro: ERROS_REGISTRADOS += 1
    print(f"[{agora}] {prefixo} {mensagem}")

def atualizar_banco_central():
    registrar_log("A atualizar Banco Central...")
    try:
        r = requests.get("https://brasilapi.com.br/api/taxas/v1", timeout=10)
        if r.status_code == 200:
            dados = r.json()
            selic = next((float(t['valor']) for t in dados if t['nome'] == 'Selic'), 0.0)
            ipca_12m = next((float(t['valor']) for t in dados if t['nome'] == 'IPCA'), 0.0)
            
            hoje = datetime.now().date()
            # Calendário prolongado (2026 e 2027)
            reunioes_copom = [
                datetime(2026, 1, 28).date(), datetime(2026, 3, 18).date(), datetime(2026, 4, 29).date(),
                datetime(2026, 6, 17).date(), datetime(2026, 8, 5).date(), datetime(2026, 9, 16).date(),
                datetime(2026, 11, 4).date(), datetime(2026, 12, 9).date(),
                datetime(2027, 1, 27).date(), datetime(2027, 3, 17).date(), datetime(2027, 5, 5).date(),
                datetime(2027, 6, 16).date(), datetime(2027, 8, 4).date(), datetime(2027, 9, 15).date(),
                datetime(2027, 11, 3).date(), datetime(2027, 12, 8).date()
            ]
            prox_copom = next((d for d in reunioes_copom if d >= hoje), reunioes_copom[-1])
            
            pd.DataFrame([{'selic': selic, 'prox_copom': prox_copom, 'ipca_12m': ipca_12m}]).to_csv("bunker_bcb.csv", index=False)
        else:
            registrar_log(f"Status incorreto na BrasilAPI: {r.status_code}", erro=True)
    except Exception as e:
        registrar_log(f"Falha total no BCB: {e}", erro=True)

def atualizar_noticias():
    registrar_log("A descarregar Notícias...")
    fontes = {
        "InfoMoney": "https://www.infomoney.com.br/feed/",
        "Investing": "https://br.investing.com/rss/news_25.rss",
        "Money Times": "https://www.moneytimes.com.br/feed/",
        "Seu Dinheiro": "https://www.seudinheiro.com/feed/"
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    palavras_proibidas = ['futebol', 'copa', 'corinthians', 'vasco', 'palmeiras', 'flamengo', 'fofoca', 'bbb']
    todas_noticias = []
    
    for nome, url in fontes.items():
        try:
            r = requests.get(url, headers=headers, timeout=10)
            root = ET.fromstring(r.content)
            contador = 0
            for item in root.findall('./channel/item'):
                titulo = item.find('title').text
                if not any(p in titulo.lower() for p in palavras_proibidas):
                    todas_noticias.append({'fonte': nome, 'titulo': titulo, 'link': item.find('link').text})
                    contador += 1
                if contador >= 8: break
        except Exception as e:
            registrar_log(f"Erro RSS {nome}: {e}", erro=True)
            
    if todas_noticias:
        pd.DataFrame(todas_noticias).to_csv("bunker_noticias.csv", index=False)

def atualizar_after_market_e_macro():
    registrar_log("A acionar TradingView...")
    try:
        tv = TvDatafeed()
    except Exception as e:
        registrar_log(f"Falha de login TV: {e}", erro=True)
        return

    # 1. After Market Otimizado (Correção de Lógica)
    ls_after = []
    for bdr, info in bdr_setup_home.items():
        try:
            # Puxa barras horárias para encontrar a diferença exata entre regular e estendida
            df = tv.get_hist(symbol=info['us'], exchange=info['exchange'], interval=Interval.in_1_hour, n_bars=24, extended_session=True)
            if df is not None and len(df) > 5:
                fecho_hj = df['close'].iloc[-1]
                # Estima o último fechamento regular filtrando os horários comerciais
                df_reg = tv.get_hist(symbol=info['us'], exchange=info['exchange'], interval=Interval.in_daily, n_bars=2)
                fecho_ontem = df_reg['close'].iloc[-1] if not df_reg.empty else fecho_hj
                
                var = ((fecho_hj / fecho_ontem) - 1) * 100
                ls_after.append({
                    'BDR (B3)': bdr, 'Ticker EUA': info['us'], 
                    'Fecho Oficial': f"$ {fecho_ontem:.2f}", 'Preço Atual': f"$ {fecho_hj:.2f}", 
                    'Variação (%)': f"{var:.2f}%", '_var_raw': var
                })
        except Exception as e:
            registrar_log(f"Erro After {info['us']}", erro=True)
        time.sleep(0.3) 
            
    if ls_after: pd.DataFrame(ls_after).to_csv("bunker_after_market.csv", index=False)

    # 2. Macro (Correção idêntica de fechamento)
    macros = {
        'IBOV': {'symbol': 'IBOV', 'exchange': 'BMFBOVESPA', 'nome': 'IBOVESPA', 'prefix': 'pts', 'formato': '{:,.0f}', 'url': '...'},
        'WIN': {'symbol': 'WIN1!', 'exchange': 'BMFBOVESPA', 'nome': 'Mini Índice', 'prefix': 'pts', 'formato': '{:,.0f}', 'url': '...'},
        'WDO': {'symbol': 'WDO1!', 'exchange': 'BMFBOVESPA', 'nome': 'Mini Dólar', 'prefix': 'R$', 'formato': '{:.2f}', 'url': '...'},
        'US10Y': {'symbol': 'US10Y', 'exchange': 'TVC', 'nome': 'Treasury 10Y', 'prefix': '%', 'formato': '{:.3f}', 'url': '...'},
        'SP500F': {'symbol': 'US500', 'exchange': 'CAPITALCOM', 'nome': 'S&P 500', 'prefix': 'pts', 'formato': '{:,.2f}', 'url': '...'}
    }
    
    resultados = []
    for chave, config in macros.items():
        try:
            df_diario = tv.get_hist(symbol=config['symbol'], exchange=config['exchange'], interval=Interval.in_daily, n_bars=3)
            if df_diario is not None and not df_diario.empty:
                fecho_anterior = df_diario['close'].iloc[-2]
                fecho_atual = df_diario['close'].iloc[-1]
                var = ((fecho_atual / fecho_anterior) - 1) * 100
                resultados.append({
                    'nome': config['nome'], 'valor': f"{config['prefix']} {config['formato'].format(fecho_atual)}", 
                    'variacao': var, 'url': config['url']
                })
        except Exception as e:
            registrar_log(f"Erro Macro {config['symbol']}", erro=True)
        time.sleep(0.3)
        
    if resultados: pd.DataFrame(resultados).to_csv("bunker_macro.csv", index=False)

def atualizar_cotacoes_b3():
    registrar_log("A atualizar B3 (Modo Incremental Inteligente)...")
    todos_ativos = list(set([a.replace('.SA', '') for a in (bdrs_elite + ibrx_selecao)]))
    for cat in etfs_master.values(): todos_ativos.extend(list(cat.keys()))
    todos_ativos = list(set(todos_ativos))
    
    for ativo in todos_ativos:
        try:
            nome_arquivo = f"{ativo}.csv"
            # Se o CSV já existe, puxa apenas 5 dias do Yahoo para poupar a API
            if os.path.exists(nome_arquivo):
                df_antigo = pd.read_csv(nome_arquivo, index_col=0, parse_dates=True)
                df_novo = yf.Ticker(f"{ativo}.SA").history(period="5d", interval="1d")
                if not df_novo.empty:
                    df_novo.index = pd.to_datetime(df_novo.index, utc=True).tz_localize(None)
                    df_novo.columns = [str(c).strip().capitalize() for c in df_novo.columns]
                    # Combina e remove os dias duplicados, mantendo o mais recente
                    df_atualizado = pd.concat([df_antigo, df_novo]).dropna(subset=['Close'])
                    df_atualizado = df_atualizado[~df_atualizado.index.duplicated(keep='last')].sort_index()
                    df_atualizado.to_csv(nome_arquivo)
            else:
                # Se for a primeira vez (ou se o CSV foi apagado), puxa 2 anos
                df_novo = yf.Ticker(f"{ativo}.SA").history(period="2y", interval="1d")
                if not df_novo.empty:
                    df_novo.index = pd.to_datetime(df_novo.index, utc=True).tz_localize(None)
                    df_novo.columns = [str(c).strip().capitalize() for c in df_novo.columns]
                    df_novo.to_csv(nome_arquivo)
                    
            time.sleep(0.2) 
        except Exception as e:
            registrar_log(f"Erro ao descarregar {ativo}", erro=True)

if __name__ == "__main__":
    registrar_log("=== A INICIAR TURNO DO OPERÁRIO OFFLINE ===")
    atualizar_banco_central()
    atualizar_noticias()
    atualizar_after_market_e_macro()
    atualizar_cotacoes_b3()
    
    if ERROS_REGISTRADOS > 15:
        registrar_log(f"🚨 ALERTA CRÍTICO: {ERROS_REGISTRADOS} falhas de extração detectadas.", erro=True)
        # O sys.exit(1) força o GitHub Actions a reportar "Failed" (ícone vermelho) para que você seja alertado.
        sys.exit(1)
        
    registrar_log("=== TURNO CONCLUÍDO. BUNKER ABASTECIDO. ===")
