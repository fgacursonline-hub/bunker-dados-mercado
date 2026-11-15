import pandas as pd
import yfinance as yf
from tvDatafeed import TvDatafeed, Interval
import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime, timedelta, timezone
import os

# Importa as listas do seu ficheiro de configuração
try:
    from config_ativos import bdrs_elite, ibrx_selecao, bdr_setup_home, etfs_master
except ImportError:
    print("Aviso: config_ativos.py não encontrado. Utilizando listas vazias para evitar erros.")
    bdrs_elite, ibrx_selecao, bdr_setup_home, etfs_master = [], [], {}, {}

def registrar_log(mensagem):
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print(f"[{agora}] {mensagem}")

def atualizar_banco_central():
    registrar_log("A atualizar Banco Central (Selic/IPCA)...")
    try:
        r = requests.get("https://brasilapi.com.br/api/taxas/v1", timeout=10)
        selic, ipca_12m = 0.0, 0.0
        if r.status_code == 200:
            dados = r.json()
            for taxa in dados:
                if taxa['nome'] == 'Selic': selic = float(taxa['valor'])
                if taxa['nome'] == 'IPCA': ipca_12m = float(taxa['valor'])
        
        hoje = datetime.now().date()
        reunioes_2026 = [
            datetime(2026, 1, 28).date(), datetime(2026, 3, 18).date(), datetime(2026, 4, 29).date(),
            datetime(2026, 6, 17).date(), datetime(2026, 8, 5).date(), datetime(2026, 9, 16).date(),
            datetime(2026, 11, 4).date(), datetime(2026, 12, 9).date()
        ]
        prox_copom = next((d for d in reunioes_2026 if d >= hoje), None)
        
        df_bcb = pd.DataFrame([{'selic': selic, 'prox_copom': prox_copom, 'ipca_12m': ipca_12m}])
        df_bcb.to_csv("bunker_bcb.csv", index=False)
    except Exception as e:
        registrar_log(f"Erro BCB: {e}")

def atualizar_noticias():
    registrar_log("A descarregar Notícias (RSS)...")
    fontes = {
        "InfoMoney": "https://www.infomoney.com.br/feed/",
        "Investing": "https://br.investing.com/rss/news_25.rss",
        "Money Times": "https://www.moneytimes.com.br/feed/",
        "Seu Dinheiro": "https://www.seudinheiro.com/feed/",
        "G1 Economia": "https://g1.globo.com/rss/g1/economia/"
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    palavras_proibidas = ['futebol', 'copa', 'assistir', 'corinthians', 'vasco', 'palmeiras', 'flamengo', 'brasileirão', 'fofoca', 'bbb', 'novela', 'filme']
    
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
            time.sleep(1)
        except Exception as e:
            registrar_log(f"Erro ao descarregar {nome}: {e}")
            
    if todas_noticias:
        pd.DataFrame(todas_noticias).to_csv("bunker_noticias.csv", index=False)

def atualizar_after_market_e_macro():
    registrar_log("A ler After-Market e Macro (TradingView)...")
    try:
        # Inicializa o TradingView (Guest Mode)
        tv = TvDatafeed()
    except Exception as e:
        registrar_log(f"Falha ao iniciar TVDatafeed: {e}")
        return

    # 1. Atualizar After Market
    ls_after = []
    if bdr_setup_home:
        for bdr, info in bdr_setup_home.items():
            try:
                df_reg = tv.get_hist(symbol=info['us'], exchange=info['exchange'], interval=Interval.in_daily, n_bars=2)
                fecho_reg = df_reg['close'].iloc[-2] if (df_reg is not None and len(df_reg) >= 2) else None
                
                preco_at = None
                if fecho_reg:
                    df_ext = tv.get_hist(symbol=info['us'], exchange=info['exchange'], interval=Interval.in_15_minute, n_bars=2, extended_session=True)
                    if df_ext is not None and not df_ext.empty:
                        preco_at = df_ext['close'].iloc[-1]
                    else:
                        df_fb = tv.get_hist(symbol=info['us'], exchange=info['exchange'], interval=Interval.in_15_minute, n_bars=2)
                        if df_fb is not None and not df_fb.empty: preco_at = df_fb['close'].iloc[-1]

                if fecho_reg and preco_at:
                    var = ((preco_at / fecho_reg) - 1) * 100
                    ls_after.append({
                        'BDR (B3)': bdr, 'Ticker EUA': info['us'], 
                        'Fecho Oficial': f"$ {fecho_reg:.2f}", 'Preço Atual': f"$ {preco_at:.2f}", 
                        'Variação (%)': f"+{var:.2f}%" if var > 0 else f"{var:.2f}%", '_var_raw': var
                    })
            except Exception as e:
                registrar_log(f"Erro After-Market {info['us']}: {e}")
            time.sleep(0.5) 
            
    if ls_after:
        pd.DataFrame(ls_after).to_csv("bunker_after_market.csv", index=False)
        registrar_log("bunker_after_market.csv gerado com sucesso.")

    # 2. Atualizar Macro Global
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
        'VIX': {'symbol': 'VIX', 'exchange': 'CBOE', 'nome': 'Índice VIX (Medo)', 'prefix': 'pts', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=CBOE%3AVIX', 'help': '**VIX Americano**...'},
        'US10Y': {'symbol': 'US10Y', 'exchange': 'TVC', 'nome': 'Treasury 10Y (EUA)', 'prefix': '%', 'formato': '{:.3f}', 'url': 'https://br.tradingview.com/chart/?symbol=TVC%3AUS10Y', 'help': '**Títulos do Tesouro**...'},
        'DXY': {'symbol': 'DXY', 'exchange': 'TVC', 'nome': 'DXY (Índice Dólar)', 'prefix': 'pts', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=TVC%3ADXY', 'help': '**Força do Dólar**...'},
        'SP500F': {'symbol': 'US500', 'exchange': 'CAPITALCOM', 'nome': 'S&P 500 (CFD)', 'prefix': 'pts', 'formato': '{:,.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=CAPITALCOM%3AUS500', 'help': '**S&P 500**...'},
        'NASF': {'symbol': 'US100', 'exchange': 'CAPITALCOM', 'nome': 'Nasdaq (CFD)', 'prefix': 'pts', 'formato': '{:,.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=CAPITALCOM%3AUS100', 'help': '**Nasdaq**...'},
        'VXBR': {'symbol': 'VXEWZ', 'exchange': 'CBOE', 'nome': 'VIX Brasil (VXEWZ)', 'prefix': 'pts', 'formato': '{:.2f}', 'url': 'https://br.tradingview.com/chart/?symbol=CBOE%3AVXEWZ', 'help': '**VIX Brasil**...'}
    }
    
    resultados = []
    for chave, config in macros.items():
        try:
            df_diario = tv.get_hist(symbol=config['symbol'], exchange=config['exchange'], interval=Interval.in_daily, n_bars=2)
            if df_diario is not None and len(df_diario) >= 2:
                fecho_ontem = df_diario['close'].iloc[-2]
                df_ext = tv.get_hist(symbol=config['symbol'], exchange=config['exchange'], interval=Interval.in_15_minute, n_bars=2, extended_session=True)
                
                if df_ext is not None and not df_ext.empty:
                    fecho_hj = df_ext['close'].iloc[-1]
                else:
                    fecho_hj = df_diario['close'].iloc[-1]
                    
                variacao = ((fecho_hj - fecho_ontem) / fecho_ontem) * 100
                valor_formatado = f"{config['prefix']} " + config['formato'].format(fecho_hj)
                
                resultados.append({
                    'nome': config['nome'], 'valor': valor_formatado, 
                    'variacao': variacao, 'url': config['url'], 
                    'help': config.get('help', '')
                })
        except Exception as e:
            registrar_log(f"Erro Macro {config['symbol']}: {e}")
        time.sleep(0.5)
        
    if resultados:
        pd.DataFrame(resultados).to_csv("bunker_macro.csv", index=False)
        registrar_log("bunker_macro.csv gerado com sucesso.")

def atualizar_cotacoes_b3():
    registrar_log("A atualizar históricos diários da B3 via YFinance...")
    todos_ativos = list(set([a.replace('.SA', '') for a in (bdrs_elite + ibrx_selecao)]))
    
    for cat in etfs_master.values():
        todos_ativos.extend(list(cat.keys()))
        
    todos_ativos = list(set(todos_ativos))
    
    for ativo in todos_ativos:
        try:
            df = yf.Ticker(f"{ativo}.SA").history(period="2y", interval="1d")
            if not df.empty:
                df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
                df.columns = [str(c).strip().capitalize() for c in df.columns]
                df.to_csv(f"{ativo}.csv")
            time.sleep(0.3) 
        except Exception as e:
            registrar_log(f"Erro ao atualizar {ativo}: {e}")

if __name__ == "__main__":
    registrar_log("=== A INICIAR TURNO DO OPERÁRIO OFFLINE ===")
    atualizar_banco_central()
    atualizar_noticias()
    atualizar_after_market_e_macro()
    atualizar_cotacoes_b3()
    registrar_log("=== TURNO CONCLUÍDO. BUNKER ABASTECIDO. ===")
