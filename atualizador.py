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

    # 1. After Market Otimizado
    ls_after = []
    for bdr, info in bdr_setup_home.items():
        try:
            df = tv.get_hist(symbol=info['us'], exchange=info['exchange'], interval=Interval.in_1_hour, n_bars=24, extended_session=True)
            if df is not None and len(df) > 5:
                fecho_hj = df['close'].iloc[-1]
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

    # 2. Macro (OS 15 ATIVOS ORIGINAIS RESTAURADOS)
    macros = {
        'IBOV': {'symbol': 'IBOV', 'exchange': 'BMFBOVESPA', 'nome': 'IBOVESPA', 'prefix': 'pts', 'formato': '{:,.0f}', 'url': 'https://br.tradingview.com/chart/?symbol=BMFBOVESPA%3AIBOV'},
        'WIN': {'symbol': 'WIN1!', 'exchange': 'BMFBOVESPA', 'nome': 'Mini Índice', 'prefix': 'pts', 'formato': '{:,.0f}', 'url': 'https://br.tradingview.com/chart/?symbol=BMFBOVESPA%3AWIN1%21'},
        'WDO': {'symbol': 'WDO1!', 'exchange': 'BMFBOVESPA', 'nome': 'Mini Dólar', 'prefix': 'R$', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=BMFBOVESPA%3AWDO1%21'},
        'DI1': {'symbol': 'DI11!', 'exchange': 'BMFBOVESPA', 'nome': 'Juros BR (DI1)', 'prefix': '%', 'formato': '{:.3f}', 'url': 'https://br.tradingview.com/chart/?symbol=BMFBOVESPA%3ADI11%21'},
        'EWZ': {'symbol': 'EWZ', 'exchange': 'AMEX', 'nome': 'EWZ (ETF Brasil)', 'prefix': '$', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=AMEX%3AEWZ'},
        'MINERIO': {'symbol': 'FEF2!', 'exchange': 'SGX', 'nome': 'Minério de Ferro', 'prefix': '$', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=SGX%3AFEF2%21'},
        'BRENT': {'symbol': 'BRN1!', 'exchange': 'ICEEUR', 'nome': 'Petróleo Brent', 'prefix': '$', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=ICEEUR%3ABRN1%21'},
        'GOLD': {'symbol': 'XAUUSD', 'exchange': 'OANDA', 'nome': 'Ouro (Spot)', 'prefix': '$', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=OANDA%3AXAUUSD'},
        'BTC': {'symbol': 'BTCUSD', 'exchange': 'BITSTAMP', 'nome': 'Bitcoin (BTC)', 'prefix': '$', 'formato': '{:,.0f}', 'url': 'https://br.tradingview.com/chart/?symbol=BITSTAMP%3ABTCUSD'},
        'VIX': {'symbol': 'VIX', 'exchange': 'CBOE', 'nome': 'Índice VIX (Medo)', 'prefix': 'pts', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=CBOE%3AVIX', 'help': '**VIX Americano (S&P 500)**\n\n• **Menos de 20 pontos:** Baixa volatilidade. Céu limpo.\n• **20 a 30 pontos:** Média volatilidade. Cautela.\n• **Acima de 30 pontos:** Pânico. Risco alto.'},
        'US10Y': {'symbol': 'US10Y', 'exchange': 'TVC', 'nome': 'Treasury 10Y (EUA)', 'prefix': '%', 'formato': '{:.3f}', 'url': 'https://br.tradingview.com/chart/?symbol=TVC%3AUS10Y', 'help': '**Títulos do Tesouro dos EUA (10 Anos)**\nSe a taxa subir muito, o capital foge do Brasil para os EUA (Renda Fixa segura), derrubando a nossa bolsa.'},
        'DXY': {'symbol': 'DXY', 'exchange': 'TVC', 'nome': 'DXY (Índice Dólar)', 'prefix': 'pts', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=TVC%3ADXY', 'help': '**Força Global do Dólar**\nÍndice do Dólar contra moedas fortes. DXY em alta significa Dólar ganhando poder, o que afunda as commodities e pressiona mercados emergentes.'},
        'SP500F': {'symbol': 'US500', 'exchange': 'CAPITALCOM', 'nome': 'S&P 500 (CFD)', 'prefix': 'pts', 'formato': '{:,.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=CAPITALCOM%3AUS500', 'help': '**S&P 500 (SPX)**\nO termômetro chefe do mundo. Indica o humor e a tendência do apetite a risco do mercado global antes mesmo de Nova York abrir.'},
        'NASF': {'symbol': 'US100', 'exchange': 'CAPITALCOM', 'nome': 'Nasdaq (CFD)', 'prefix': 'pts', 'formato': '{:,.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=CAPITALCOM%3AUS100', 'help': '**Nasdaq (NDX)**\nBolsa de tecnologia. Fortemente penalizada quando o Treasury 10Y sobe. É o motor da especulação de Wall Street.'},
        'VXBR': {'symbol': 'VXEWZ', 'exchange': 'CBOE', 'nome': 'VIX Brasil (VXEWZ)', 'prefix': 'pts', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=CBOE%3AVXEWZ', 'help': '**Leitura Tática de Cenário (VIX Brasil):**\n\n• **IBOV caindo + VIX Brasil subindo:** Alerta de risco\n• **IBOV subindo + VIX Brasil caindo:** Ambiente mais favorável\n• **IBOV parado + VIX Brasil subindo:** Mercado se protegendo, cuidado\n• **VIX Brasil muito baixo:** Mercado complacente, risco de susto.'}
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
                    'variacao': var, 'url': config['url'], 'help': config.get('help', '')
                })
        except Exception as e:
            registrar_log(f"Erro Macro {config['symbol']}", erro=True)
        time.sleep(0.3)
        
    if resultados: pd.DataFrame(resultados).to_csv("bunker_macro.csv", index=False)

def atualizar_cotacoes_b3():
    registrar_log("A atualizar B3 (Reconstrução Completa 5 anos para ajuste de Proventos)...")
    todos_ativos = list(set([a.replace('.SA', '') for a in (bdrs_elite + ibrx_selecao)]))
    for cat in etfs_master.values(): todos_ativos.extend(list(cat.keys()))
    todos_ativos = list(set(todos_ativos))
    
    # Criação da sessão que imita o navegador Chrome (Evita bloqueio do Yahoo)
    sessao_yf = requests.Session()
    sessao_yf.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    for ativo in todos_ativos:
        try:
            nome_arquivo = f"{ativo}.csv"
            
            # ATUALIZADO PARA 5 ANOS ("5y") COMO SOLICITADO
            ticker = yf.Ticker(f"{ativo}.SA", session=sessao_yf)
            df_novo = ticker.history(period="5y", interval="1d")
            
            if not df_novo.empty:
                df_novo.index = pd.to_datetime(df_novo.index, utc=True).tz_localize(None)
                df_novo.columns = [str(c).strip().capitalize() for c in df_novo.columns]
                df_novo.to_csv(nome_arquivo)
                
            time.sleep(0.5) 
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
        sys.exit(1)
        
    registrar_log("=== TURNO CONCLUÍDO. BUNKER ABASTECIDO. ===")
