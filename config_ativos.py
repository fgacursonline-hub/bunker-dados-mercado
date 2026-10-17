# --- CONFIGURAÇÃO CENTRAL DE ATIVOS - CAÇADORES DE ELITE ---

# 1. BDRs de Elite (Foco Internacional)
bdrs_elite = [
    'A1MD34.SA', 'A1MT34.SA', 'AAPL34.SA', 'AMZO34.SA', 'ASML34.SA',
    'AURA33.SA', 'AVGO34.SA', 'BABA34.SA', 'BERK34.SA', 'BKNG34.SA',
    'BOAC34.SA', 'BSOX39.SA', 'C2OI34.SA', 'C2RW34.SA', 'CATP34.SA',
    'COCA34.SA', 'CSCO34.SA', 'D1EL34.SA', 'F1TN34.SA', 'GOGL34.SA',
    'HPQB34.SA', 'IBMB34.SA', 'INBR34.SA', 'ITLC34.SA', 'IVVB11.SA',
    'JBSS32.SA', 'K1LA34.SA', 'L1RC34.SA', 'LILY34.SA', 'M1RN34.SA',
    'M1TA34.SA', 'M2RV34.SA', 'M2ST34.SA', 'MCDC34.SA', 'MELI34.SA',
    'MSCD34.SA', 'MSFT34.SA', 'MUTC34.SA', 'N1DA34.SA', 'N2ET34.SA',
    'NASD11.SA', 'NEXT34.SA', 'NFLX34.SA', 'NIKE34.SA', 'NVDC34.SA',
    'ORCL34.SA', 'P2AN34.SA', 'P2LT34.SA', 'QCOM34.SA', 'ROXO34.SA',
    'S1PO34.SA', 'S2HO34.SA', 'SPCX34.SA', 'SSFO34.SA', 'STOC34.SA',
    'TSLA34.SA', 'TSMC34.SA', 'U1BE34.SA', 'VISA34.SA', 'WRLD11.SA',
    'XPBR31.SA',
]

# 2. IBrX Seleção (Foco Nacional)
ibrx_selecao = [
    'ABCB4.SA', 'ABEV3.SA', 'ALLD3.SA', 'ALOS3.SA', 'ALUP11.SA', 'ANIM3.SA',
    'ASAI3.SA', 'AUAU3.SA', 'AURE3.SA', 'AXIA3.SA', 'AZZA3.SA', 'B3SA3.SA',
    'BBAS3.SA', 'BBDC4.SA', 'BBSE3.SA', 'BEEF3.SA', 'BLAU3.SA', 'BMEB4.SA',
    'BPAC11.SA', 'BRAP4.SA', 'BRAV3.SA', 'BRBI11.SA', 'BRSR6.SA', 'CASH3.SA',
    'CEAB3.SA', 'CMIG4.SA', 'CMIN3.SA', 'COGN3.SA', 'CPFE3.SA', 'CPLE3.SA',
    'CSAN3.SA', 'CSMG3.SA', 'CSNA3.SA', 'CURY3.SA', 'CVCB3.SA', 'CXSE3.SA',
    'CYRE3.SA', 'DIRR3.SA', 'DXCO3.SA', 'ECOR3.SA', 'EGIE3.SA', 'EMBJ3.SA',
    'ENEV3.SA', 'ENGI11.SA', 'EQTL3.SA', 'EZTC3.SA', 'FESA4.SA', 'FIQE3.SA',
    'FLRY3.SA', 'GGBR4.SA', 'GMAT3.SA', 'GOAU4.SA', 'GRND3.SA', 'HAPV3.SA',
    'IGTI11.SA', 'INTB3.SA', 'IRBR3.SA', 'ISAE4.SA', 'ITSA4.SA', 'ITUB4.SA',
    'JHSF3.SA', 'JSLG3.SA', 'KLBN11.SA', 'LAVV3.SA', 'LEVE3.SA', 'LIGT3.SA',
    'LOGG3.SA', 'LREN3.SA', 'LWSA3.SA', 'MBRF3.SA', 'MDIA3.SA', 'MDNE3.SA',
    'MELK3.SA', 'MGLU3.SA', 'MOTV3.SA', 'MRVE3.SA', 'MULT3.SA', 'MYPK3.SA',
    'ORVR3.SA', 'PETR4.SA', 'PGMN3.SA', 'PINE4.SA', 'PLPL3.SA', 'POMO4.SA',
    'POSI3.SA', 'PRIO3.SA', 'PSSA3.SA', 'QUAL3.SA', 'RADL3.SA', 'RANI3.SA',
    'RAPT4.SA', 'RDOR3.SA', 'RENT3.SA', 'ROMI3.SA', 'SANB11.SA', 'SAPR11.SA',
    'SBSP3.SA', 'SEER3.SA', 'SHUL4.SA', 'SIMH3.SA', 'SLCE3.SA', 'SMFT3.SA',
    'SMTO3.SA', 'SOJA3.SA', 'SUZB3.SA', 'SYNE3.SA', 'TAEE11.SA', 'TEND3.SA',
    'TFCO4.SA', 'TIMS3.SA', 'TOTS3.SA', 'TUPY3.SA', 'UGPA3.SA', 'UNIP6.SA',
    'USIM5.SA', 'VALE3.SA', 'VAMO3.SA', 'VBBR3.SA', 'VIVA3.SA', 'VIVT3.SA',
    'VULC3.SA', 'VVEO3.SA', 'WEGE3.SA', 'YDUQ3.SA',
]

# 3. Mapeamento BDR ↔ STOCK (Para Arbitragem)
pares_elite = {
    'A1MD34': 'AMD',
    'A1MT34': 'AMAT',
    'AAPL34': 'AAPL',
    'AMZO34': 'AMZN',
    'ASML34': 'ASML',
    'AURA33': 'AUGO',
    'AVGO34': 'AVGO',
    'BABA34': 'BABA',
    'BERK34': 'BRK.B',
    'BKNG34': 'BKNG',
    'BOAC34': 'BAC',
    'BSOX39': 'SOXX',
    'C2OI34': 'COIN',
    'C2RW34': 'CRWD',
    'CATP34': 'CAT',
    'COCA34': 'KO',
    'CSCO34': 'CSCO',
    'D1EL34': 'DELL',
    'F1TN34': 'FTNT',
    'GOGL34': 'GOOGL',
    'HPQB34': 'HPQ',
    'IBMB34': 'IBM',
    'INBR34': 'INTR',
    'ITLC34': 'INTC',
    'IVVB11': 'IVV',     # ETF de referência no exterior
    'JBSS32': 'JBS',
    'K1LA34': 'KLAC',
    'L1RC34': 'LRCX',
    'LILY34': 'LLY',
    'M1RN34': 'MRNA',
    'M1TA34': 'META',
    'M2RV34': 'MRVL',
    'M2ST34': 'MSTR',
    'MCDC34': 'MCD',
    'MELI34': 'MELI',
    'MSCD34': 'MA',
    'MSFT34': 'MSFT',
    'MUTC34': 'MU',
    'N1DA34': 'NDAQ',
    'N2ET34': 'NET',
    'NASD11': 'QQQ',     # ETF de referência no exterior
    'NEXT34': 'NEE',
    'NFLX34': 'NFLX',
    'NIKE34': 'NKE',
    'NVDC34': 'NVDA',
    'ORCL34': 'ORCL',
    'P2AN34': 'PANW',
    'P2LT34': 'PLTR',
    'QCOM34': 'QCOM',
    'ROXO34': 'NU',
    'S1PO34': 'SPOT',
    'S2HO34': 'SHOP',
    'SPCX34': 'SPCX',
    'SSFO34': 'CRM',
    'STOC34': 'STNE',
    'TSLA34': 'TSLA',
    'TSMC34': 'TSM',
    'U1BE34': 'UBER',
    'VISA34': 'V',
    'WRLD11': 'VT',      # ETF de referência no exterior
    'XPBR31': 'XP',
}

# 4. Índices e Benchmarks Setoriais (Termômetros do Mercado)
benchmarks_elite = [
    'IBOV',    # Índice Bovespa Principal
    'SMLL',    # Índice de Small Caps
    'IFNC',    # Índice Financeiro (Bancos)
    'IMAT',    # Índice de Materiais Básicos (Commodities)
    'IEEX',    # Índice de Energia Elétrica
    'UTIL',    # Índice Utilidade Pública (Energia e Saneamento)
    'ICON',    # Índice de Consumo e Varejo
    'IMOB',    # Índice Imobiliário (Construtoras e Shoppings)
    'INDX',    # Índice Industrial
    'AGRO',    # Índice do Agronegócio
    'IFIX',    # Índice de Fundos Imobiliários
    'BOVA11',  # ETF do Ibovespa
    'IVVB11'   # ETF do S&P 500 (EUA) negociado no Brasil
]

# 5. Ativos Macro e Futuros (Comparação Global)
# Dicionário mapeia: 'Símbolo': 'Bolsa de Origem'
macro_elite = {
    'DXY': 'TVC',          # Índice Dólar
    'WDO1!': 'BMFBOVESPA', # Mini Dólar Futuro Contínuo
    'WIN1!': 'BMFBOVESPA', # Mini Índice Futuro Contínuo
    'BIT1!': 'BMFBOVESPA', # Bitcoin Futuro B3 (Variação Financeira)
    'DI1!': 'BMFBOVESPA',  # Taxa DI Futuro
    'FEF2!': 'SGX',        # Minério de Ferro (Singapura)
    'BRN1!': 'ICEEUR',     # Petróleo Brent Contínuo
    'XAUUSD': 'OANDA',     # Ouro Global
    'EWZ': 'AMEX',         # ETF MSCI Brazil
    'BTCUSDT': 'BINANCE'   # Bitcoin vs Tether (Referência Cripto Global)
}

bdr_setup_home = {
    'A1MD34': {'us': 'AMD', 'exchange': 'NASDAQ'},
    'A1MT34': {'us': 'AMAT', 'exchange': 'NASDAQ'},
    'AAPL34': {'us': 'AAPL', 'exchange': 'NASDAQ'},
    'AMZO34': {'us': 'AMZN', 'exchange': 'NASDAQ'},
    'ASML34': {'us': 'ASML', 'exchange': 'NASDAQ'},
    'AURA33': {'us': 'AUGO', 'exchange': 'NASDAQ'},
    'AVGO34': {'us': 'AVGO', 'exchange': 'NASDAQ'},
    'BABA34': {'us': 'BABA', 'exchange': 'NYSE'},
    'BERK34': {'us': 'BRK.B', 'exchange': 'NYSE'},
    'BKNG34': {'us': 'BKNG', 'exchange': 'NASDAQ'},
    'BOAC34': {'us': 'BAC', 'exchange': 'NYSE'},
    'BSOX39': {'us': 'SOXX', 'exchange': 'NASDAQ'},
    'C2OI34': {'us': 'COIN', 'exchange': 'NASDAQ'},
    'C2RW34': {'us': 'CRWD', 'exchange': 'NASDAQ'},
    'CATP34': {'us': 'CAT', 'exchange': 'NYSE'},
    'COCA34': {'us': 'KO', 'exchange': 'NYSE'},
    'CSCO34': {'us': 'CSCO', 'exchange': 'NASDAQ'},
    'D1EL34': {'us': 'DELL', 'exchange': 'NYSE'},
    'F1TN34': {'us': 'FTNT', 'exchange': 'NASDAQ'},
    'GOGL34': {'us': 'GOOGL', 'exchange': 'NASDAQ'},
    'HPQB34': {'us': 'HPQ', 'exchange': 'NYSE'},
    'IBMB34': {'us': 'IBM', 'exchange': 'NYSE'},
    'INBR34': {'us': 'INTR', 'exchange': 'NASDAQ'},
    'ITLC34': {'us': 'INTC', 'exchange': 'NASDAQ'},
    'IVVB11': {'us': 'IVV', 'exchange': 'AMEX'},  # NYSE Arca
    'JBSS32': {'us': 'JBS', 'exchange': 'NYSE'},
    'K1LA34': {'us': 'KLAC', 'exchange': 'NASDAQ'},
    'L1RC34': {'us': 'LRCX', 'exchange': 'NASDAQ'},
    'LILY34': {'us': 'LLY', 'exchange': 'NYSE'},
    'M1RN34': {'us': 'MRNA', 'exchange': 'NASDAQ'},
    'M1TA34': {'us': 'META', 'exchange': 'NASDAQ'},
    'M2RV34': {'us': 'MRVL', 'exchange': 'NASDAQ'},
    'M2ST34': {'us': 'MSTR', 'exchange': 'NASDAQ'},
    'MCDC34': {'us': 'MCD', 'exchange': 'NYSE'},
    'MELI34': {'us': 'MELI', 'exchange': 'NASDAQ'},
    'MSCD34': {'us': 'MA', 'exchange': 'NYSE'},
    'MSFT34': {'us': 'MSFT', 'exchange': 'NASDAQ'},
    'MUTC34': {'us': 'MU', 'exchange': 'NASDAQ'},
    'N1DA34': {'us': 'NDAQ', 'exchange': 'NASDAQ'},
    'N2ET34': {'us': 'NET', 'exchange': 'NYSE'},
    'NASD11': {'us': 'QQQ', 'exchange': 'NASDAQ'},
    'NEXT34': {'us': 'NEE', 'exchange': 'NYSE'},
    'NFLX34': {'us': 'NFLX', 'exchange': 'NASDAQ'},
    'NIKE34': {'us': 'NKE', 'exchange': 'NYSE'},
    'NVDC34': {'us': 'NVDA', 'exchange': 'NASDAQ'},
    'ORCL34': {'us': 'ORCL', 'exchange': 'NYSE'},
    'P2AN34': {'us': 'PANW', 'exchange': 'NASDAQ'},
    'P2LT34': {'us': 'PLTR', 'exchange': 'NASDAQ'},
    'QCOM34': {'us': 'QCOM', 'exchange': 'NASDAQ'},
    'ROXO34': {'us': 'NU', 'exchange': 'NYSE'},
    'S1PO34': {'us': 'SPOT', 'exchange': 'NYSE'},
    'S2HO34': {'us': 'SHOP', 'exchange': 'NASDAQ'},
    'SPCX34': {'us': 'SPCX', 'exchange': 'NASDAQ'},
    'SSFO34': {'us': 'CRM', 'exchange': 'NYSE'},
    'STOC34': {'us': 'STNE', 'exchange': 'NASDAQ'},
    'TSLA34': {'us': 'TSLA', 'exchange': 'NASDAQ'},
    'TSMC34': {'us': 'TSM', 'exchange': 'NYSE'},
    'U1BE34': {'us': 'UBER', 'exchange': 'NYSE'},
    'VISA34': {'us': 'V', 'exchange': 'NYSE'},
    'WRLD11': {'us': 'VT', 'exchange': 'AMEX'},  # NYSE Arca
    'XPBR31': {'us': 'XP', 'exchange': 'NASDAQ'},
}


etfs_master = {
    "ETFs Brasil": {
        "BOVA11": {"replica": "Ibovespa B3", "desc": "Principal ETF do Ibov. Serve como termômetro da bolsa brasileira.", "ativos": "Vale, Petrobras, Itaú, BBDC, B3"},
        "BOVV11": {"replica": "Ibovespa B3", "desc": "Alternativa ao BOVA11, também acompanha o Ibovespa.", "ativos": "Vale, Petrobras, Itaú, BBDC, B3"},
        "PIBB11": {"replica": "IBrX 50 B3", "desc": "As 50 ações mais negociadas e representativas da B3.", "ativos": "Petrobras, Vale, Itaú, Ambev, B3"},
        "BRAX11": {"replica": "IBrX 100 B3", "desc": "As 100 ações mais negociadas e representativas do mercado brasileiro.", "ativos": "Vale, Petrobras, Itaú, WEG, Localiza"},
        "SMAL11": {"replica": "SMLL (Small Caps B3)", "desc": "Empresas de menor capitalização. Bom para ver apetite ao risco local.", "ativos": "Embraer, Azul, Santos Brasil, São Martinho, PRIO"},
        "DIVO11": {"replica": "IDIV B3 (Dividendos)", "desc": "Empresas boas pagadoras de dividendos/JCP.", "ativos": "Taesa, Engie, BB Seguridade, CPFL, Vivo"},
        "DIVD11": {"replica": "IDIV B3 (Mensal)", "desc": "Parecido com DIVO11, mas com proposta de distribuição mensal de dividendos.", "ativos": "Taesa, Engie, BB Seguridade, CPFL, Vivo"}
    },
    "ETFs Setoriais Brasil": {
        "FIND11": {"replica": "IFNC B3", "desc": "Bancos, fintechs, seguradoras e setor financeiro brasileiro.", "ativos": "Itaú, Bradesco, B3, Nubank, Banco do Brasil"},
        "MATB11": {"replica": "IMAT B3 (Materiais Básicos)", "desc": "Mineração, siderurgia, papel e celulose, química e commodities brasileiras.", "ativos": "Vale, Suzano, Klabin, Gerdau, CSN"},
        "TECB11": {"replica": "Ações Tech Brasil", "desc": "Empresas brasileiras de tecnologia, e-commerce, software, dados.", "ativos": "Mercado Livre, Stone, Totvs, Locaweb, Linx"}
    },
    "Internacionais negociados na B3": {
        "IVVB11": {"replica": "S&P 500 (em reais)", "desc": "500 grandes empresas dos EUA.", "ativos": "Nvidia, Apple, Microsoft, Amazon, Alphabet"},
        "SPXI11": {"replica": "S&P 500", "desc": "Alternativa ao IVVB11, gerida pelo Itaú.", "ativos": "Nvidia, Apple, Microsoft, Amazon, Alphabet"},
        "NASD11": {"replica": "Nasdaq-100", "desc": "Grandes empresas não financeiras da Nasdaq, forte peso em tecnologia.", "ativos": "Nvidia, Apple, Broadcom, Tesla, Alphabet"},
        "WRLD11": {"replica": "FTSE Global All Cap", "desc": "Bolsa global, países desenvolvidos e emergentes.", "ativos": "Apple, Microsoft, Nvidia, TSMC, Tencent"},
        "ACWI11": {"replica": "MSCI ACWI", "desc": "Ações globais de países desenvolvidos e emergentes.", "ativos": "Apple, Microsoft, Nvidia, Amazon, Meta"}
    },
    "BDRs de ETFs Americanos e Globais": {
        "BIVB39": {"replica": "S&P 500 (iShares)", "desc": "Grandes empresas dos EUA.", "ativos": "Nvidia, Apple, Microsoft, Amazon, Alphabet"},
        "BSOX39": {"replica": "ICE Semiconductor Index", "desc": "Semicondutores.", "ativos": "Broadcom, Nvidia, Applied Materials, Lam Research, Intel"},
        "BIYW39": {"replica": "U.S. Technology", "desc": "Tecnologia americana: software, semicondutores e hardware.", "ativos": "Apple, Microsoft, Nvidia, Broadcom, Cisco"},
        "BIYE39": {"replica": "U.S. Energy", "desc": "Energia, petróleo e gás dos EUA.", "ativos": "Exxon, Chevron, ConocoPhillips, EOG, Schlumberger"},
        "BIYF39": {"replica": "U.S. Financials", "desc": "Bancos e financeiras dos EUA.", "ativos": "JPMorgan, Berkshire Hathaway, Bank of America, Wells Fargo"},
        "BIXJ39": {"replica": "Global Healthcare", "desc": "Saúde global.", "ativos": "Eli Lilly, Novo Nordisk, J&J, Merck, AbbVie"},
        "BIGF39": {"replica": "Global Infrastructure", "desc": "Infraestrutura global.", "ativos": "NextEra, Union Pacific, American Tower, Enbridge, Duke"},
        "BEEM39": {"replica": "MSCI Emerging Markets", "desc": "Mercados emergentes.", "ativos": "TSMC, Tencent, Alibaba, Samsung, Reliance"},
        "BEWU39": {"replica": "MSCI United Kingdom", "desc": "Reino Unido.", "ativos": "Shell, AstraZeneca, HSBC, Unilever, BP"},
        "BQQW39": {"replica": "Nasdaq-100 Equal Weighted", "desc": "Nasdaq-100 com pesos iguais, reduzindo concentração nas gigantes.", "ativos": "Meta, Intel, Netflix, PepsiCo, Adobe"}
    },
    "Commodities, Ouro e Cripto": {
        "GOLD11": {"replica": "LBMA Gold Price", "desc": "Ouro em reais. Ajuda em momentos de aversão a risco e dólar forte.", "ativos": "Ouro físico, Contratos atrelados ao Ouro"},
        "GOLB11": {"replica": "Índice Futuro de Ouro B3", "desc": "Ouro via índice futuro da B3.", "ativos": "Contratos futuros BMF Ouro"},
        "HASH11": {"replica": "Nasdaq Crypto Index", "desc": "Cesta de criptoativos.", "ativos": "Bitcoin, Ethereum, Solana, Chainlink, Litecoin"},
        "QBTC11": {"replica": "Bitcoin", "desc": "Exposição direta a BTC.", "ativos": "Bitcoin"},
        "QETH11": {"replica": "Ethereum", "desc": "Exposição direta a ETH.", "ativos": "Ethereum"}
    },
    "Renda Fixa e Juros": {
        "IMAB11": {"replica": "IMA-B", "desc": "Títulos públicos indexados ao IPCA. Mostra juro real/inflacionário.", "ativos": "Tesouro IPCA+ Vários Vencimentos"},
        "B5P211": {"replica": "IMA-B5 P2", "desc": "IPCA+ mais curto, vencimentos até cerca de 5 anos.", "ativos": "Tesouro IPCA+ Curto Prazo"},
        "IRFM11": {"replica": "IRF-M P2", "desc": "Títulos prefixados. Sensível à curva de juros.", "ativos": "Tesouro Prefixado"},
        "LFTS11": {"replica": "Teva Tesouro Selic", "desc": "Títulos pós-fixados ligados à Selic.", "ativos": "LFT (Tesouro Selic)"},
        "FIXA11": {"replica": "Futuros DI 3 anos", "desc": "Exposição à curva de DI/futuros de juros.", "ativos": "Contratos Futuros DI"},
        "BDAP11": {"replica": "DAP5 B3", "desc": "Cupom de IPCA/futuro de juro real.", "ativos": "Futuros de Cupom de IPCA"}
    }
}
