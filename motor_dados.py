"""
motor_dados.py  (APP PÚBLICO)

Lê os CSVs do Bunker que ficam na MESMA PASTA deste arquivo (raiz do repositório
do app). Não faz nenhuma chamada de rede: o número de usuários não afeta
bloqueio de GitHub/Yahoo. Quem atualiza os CSVs é o robô privado
(robo_atualizacao.py), nunca o Streamlit.

API:
  puxar_dados_com_erro(ativo, tempo_grafico, barras) -> (DataFrame, mensagem_de_erro)
  puxar_dados_blindados(ativo, tempo_grafico, barras) -> DataFrame ou None  (compatível com o código antigo)

Tempos: "1d", "1wk", "1mo" (qualquer ativo) e "15m", "60m" (só futuros WIN/WDO,
com CSV intraday exportado do Profit/MT5).
"""
import os
import re

import pandas as pd
import streamlit as st

# ============================================================
# CONFIGURACAO
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTAS_BUSCA = [BASE_DIR, os.getcwd()]     # raiz do projeto primeiro; pasta de execução como reserva
TTL_SEGUNDOS = 3600                        # a chave inclui a data do arquivo: CSV novo é lido na hora
COLUNAS_OHLC = ["Open", "High", "Low", "Close"]
TEMPOS_DIARIOS = ("1d", "1wk", "1mo")
TEMPOS_INTRADAY = ("15m", "60m")
_NOME_VALIDO = re.compile(r"[A-Z0-9!_\-]{1,20}")

# CSVs nacionais (Profit) costumam vir com cabeçalho em português
_RENOMEAR = {
    "Abertura": "Open", "Maxima": "High", "Máxima": "High", "Minima": "Low", "Mínima": "Low",
    "Fechamento": "Close", "Ultimo": "Close", "Último": "Close", "Fechamento ajustado": "Adj close",
}


class ErroBunker(Exception):
    pass


def _freq_mensal():
    """'ME' no pandas >= 2.2; 'M' nas versões anteriores."""
    try:
        major, minor = (int(x) for x in pd.__version__.split(".")[:2])
        return "ME" if (major, minor) >= (2, 2) else "M"
    except Exception:
        return "ME"


_FREQ = {"1wk": "W-FRI", "1mo": _freq_mensal()}


def _eh_futuro(ativo_limpo):
    return ativo_limpo.startswith(("WIN", "WDO"))


# ============================================================
# LEITURA DO CSV
# ============================================================

def _localizar(ativo_limpo):
    for pasta in PASTAS_BUSCA:
        caminho = os.path.join(pasta, f"{ativo_limpo}.csv")
        if os.path.isfile(caminho):
            return caminho
    return None


def _ler_csv(caminho, ativo_limpo):
    # Detecta o formato pelo cabeçalho: nacional (Profit) usa ";" + vírgula decimal + dd/mm/aaaa
    def _abrir(**kw):
        try:
            return pd.read_csv(caminho, index_col=0, encoding="utf-8-sig", **kw)
        except UnicodeDecodeError:
            return pd.read_csv(caminho, index_col=0, encoding="latin-1", **kw)

    try:
        with open(caminho, "r", encoding="utf-8-sig", errors="replace") as f:
            cabecalho = f.readline()
    except OSError as exc:
        raise ErroBunker(f"Não foi possível abrir {ativo_limpo}.csv ({exc}).")

    dayfirst = cabecalho.count(";") > cabecalho.count(",")
    df = _abrir(sep=";", decimal=",") if dayfirst else _abrir()

    df.columns = [_RENOMEAR.get(str(c).strip().capitalize(), str(c).strip().capitalize()) for c in df.columns]

    faltando = [c for c in COLUNAS_OHLC if c not in df.columns]
    if faltando:
        raise ErroBunker(f"{ativo_limpo}.csv sem as colunas {faltando}.")
    if "Volume" not in df.columns:
        df["Volume"] = 0.0

    df.index = pd.to_datetime(df.index, utc=True, errors="coerce", dayfirst=dayfirst).tz_localize(None)
    df = df[~df.index.isna()]
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df[COLUNAS_OHLC + ["Volume"]].apply(pd.to_numeric, errors="coerce").dropna(subset=COLUNAS_OHLC)

    # Diário: o robô grava em UTC (00:00-03:00 vira 03:00). Se há 1 barra por dia, fica só a data.
    if df.index.normalize().is_unique:
        df.index = df.index.normalize()
    df.index.name = "Date"

    if len(df) < 2:
        raise ErroBunker(f"{ativo_limpo}.csv tem histórico insuficiente ({len(df)} linha).")
    return df


@st.cache_data(ttl=TTL_SEGUNDOS, max_entries=1000, show_spinner=False)
def _carregar_arquivo(caminho, mtime, ativo_limpo):
    """Cache compartilhado entre TODAS as sessões. `mtime` na chave: arquivo novo = leitura nova."""
    return _ler_csv(caminho, ativo_limpo)


# ============================================================
# CONVERSAO DE TEMPO GRAFICO
# ============================================================

def _converter_tempo(df, tempo_grafico):
    if tempo_grafico not in _FREQ:
        return df

    freq = _FREQ[tempo_grafico]
    agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
    out = df.resample(freq).agg(agg).dropna(subset=["Close"])
    # A vela leva a data do ÚLTIMO PREGÃO real do período (não domingo nem dia 1)
    ultimas = df.index.to_series().resample(freq).max()
    out.index = pd.DatetimeIndex(ultimas.reindex(out.index).values, name="Date")
    return out


# ============================================================
# API PUBLICA
# ============================================================

def puxar_dados_com_erro(ativo, tempo_grafico="1d", barras=1500):
    """Devolve (DataFrame, mensagem). Em sucesso a mensagem é ''."""
    ativo_limpo = str(ativo).upper().replace(".SA", "").strip()

    if not _NOME_VALIDO.fullmatch(ativo_limpo):
        return pd.DataFrame(), f"Nome de ativo inválido: '{ativo_limpo}'."
    if tempo_grafico not in TEMPOS_DIARIOS + TEMPOS_INTRADAY:
        return pd.DataFrame(), f"Tempo gráfico '{tempo_grafico}' não suportado."
    if tempo_grafico in TEMPOS_INTRADAY and not _eh_futuro(ativo_limpo):
        return pd.DataFrame(), (
            f"Intradiário ({tempo_grafico}) só existe para WIN/WDO; o Bunker de ações é diário."
        )

    caminho = _localizar(ativo_limpo)
    if caminho is None:
        return pd.DataFrame(), f"{ativo_limpo}.csv não encontrado no Bunker."

    try:
        df = _carregar_arquivo(caminho, os.path.getmtime(caminho), ativo_limpo)
        df = _converter_tempo(df, tempo_grafico)
    except ErroBunker as exc:
        return pd.DataFrame(), str(exc)
    except Exception as exc:
        return pd.DataFrame(), f"Erro ao ler {ativo_limpo}.csv: {type(exc).__name__}: {exc}"

    if df.empty:
        return pd.DataFrame(), f"{ativo_limpo}: base vazia após conversão para {tempo_grafico}."
    return df.tail(barras).copy(), ""


def puxar_dados_blindados(ativo, tempo_grafico="1d", barras=1500, tempo_real=False):
    """Compatibilidade: devolve o DataFrame, ou None se houver qualquer problema."""
    df, erro = puxar_dados_com_erro(ativo, tempo_grafico, barras)
    return None if erro else df
