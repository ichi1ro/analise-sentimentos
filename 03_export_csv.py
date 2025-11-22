#!/usr/bin/env python3
# 04_financial_analysis.py
"""
Análise de Dados Financeiros (Passo 2) para o trabalho.

Dependências:
  pip install yfinance pandas numpy python-dateutil

Uso:
  python 04_financial_analysis.py

Pressupostos:
  - Existe um arquivo 'noticias_processadas.json' gerado pelo passo de coleta/processamento.
    (ex.: 02_process_raw.py salva esse arquivo). :contentReference[oaicite:2]{index=2}
"""

import json
from datetime import datetime, timedelta
from dateutil import parser
import pandas as pd
import numpy as np
import yfinance as yf
import os
import warnings

warnings.filterwarnings("ignore")

# ---------- CONFIGURAÇÃO -------------
INPUT_NEWS_FILE = "noticias_processadas.json"   # arquivo criado por 02_process_raw.py. :contentReference[oaicite:3]{index=3}
OUTPUT_FOLDER = "finance_analysis_output"
OUTPUT_PER_NEWS_CSV = os.path.join(OUTPUT_FOLDER, "noticias_com_precos.csv")
OUTPUT_BY_COMPANY_CSV = os.path.join(OUTPUT_FOLDER, "resumo_por_empresa.csv")

# Mapeamento empresa -> ticker B3 (modifique conforme suas empresas)
TICKER_MAP = {
    "Petrobras": "PETR4.SA",
    "PETROBRAS": "PETR4.SA",
    "Petrobras (PETR4)": "PETR4.SA",
    "Magazine Luiza": "MGLU3.SA",
    "MGLU": "MGLU3.SA",
    "Itaú Unibanco": "ITUB4.SA",
    "ITAU": "ITUB4.SA",
    "Vale": "VALE3.SA",
    "TOTVS": "TOTS3.SA",
    "Positivo Tecnologia": "POSI3.SA",
    "Locaweb": "LWSA3.SA",
    "Sinqia": "SQIA3.SA",
    # adicione outros mapeamentos conforme necessário
}

# número de dias antes/depois a capturar (já que precisamos de -2..+2)
WINDOW_BEFORE = 2
WINDOW_AFTER = 2

# buffer extra ao baixar (para cobrir feriados e fechamento de mercado)
BUFFER_DAYS = 7

# -------------------------------------


def ensure_output_folder():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def load_news(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    # data esperado: lista de dicts com chaves: empresa, titulo, url, data_publicacao, conteudo
    return data


def to_date(dt_iso):
    if not dt_iso:
        return None
    try:
        # aceita ISO com Z e sem Z
        return parser.isoparse(dt_iso)
    except Exception:
        try:
            return datetime.fromisoformat(dt_iso.replace("Z", ""))
        except Exception:
            return None


def ticker_for_company(company_name):
    # tenta mapeamento direto; se não achar, tenta variações simples
    if company_name in TICKER_MAP:
        return TICKER_MAP[company_name]
    # procurar por substring em chaves do map
    for k, v in TICKER_MAP.items():
        if k.lower() in company_name.lower() or company_name.lower() in k.lower():
            return v
    return None


def download_prices(ticker, start_date, end_date):
    """Baixa preços de ticker no intervalo [start_date, end_date] (datas datetime.date/datetime)."""
    # yfinance aceita strings
    start = (start_date - timedelta(days=BUFFER_DAYS)).strftime("%Y-%m-%d")
    end = (end_date + timedelta(days=BUFFER_DAYS)).strftime("%Y-%m-%d")
    try:
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    except Exception as e:
        # Caso o ticker esteja deslistado ou ocorra outra falha de download
        print(f"⚠️ Aviso: falha ao baixar {ticker} entre {start} e {end}: {e}")
        return pd.DataFrame()
    if df is None or df.empty:
        return df
    # garantir coluna Date como índice datetime.date
    df.index = pd.to_datetime(df.index)
    return df


def nearest_trading_day(df_index, target_date):
    """Dado índice datetime64[ns] e target_date (datetime), retorna a data do pregão mais próxima (<= target if available, else next)."""
    # procura por target_date exato
    target = pd.to_datetime(target_date).normalize()
    if target in df_index:
        return target
    # procurar o próximo pregão anterior até alguns dias (busca backward then forward)
    # backward
    prev = df_index[df_index <= target]
    if not prev.empty:
        return prev.max()
    # forward
    nxt = df_index[df_index >= target]
    if not nxt.empty:
        return nxt.min()
    return None


def compute_daily_metrics(prices_df):
    # prices_df deve conter colunas Open, High, Low, Close, Adj Close, Volume
    df = prices_df.copy()
    df["pct_change_prev_close"] = df["Close"].pct_change()  # (close - prev_close) / prev_close
    df["intraday_pct"] = (df["Close"] - df["Open"]) / df["Open"]
    return df


# helper para evitar ambiguidade de comparação com Series
def to_float_safe(v):
    # Se for uma Series, tente extrair o primeiro elemento
    if isinstance(v, pd.Series):
        if v.size == 0:
            return None
        v = v.iloc[0]
    # Agora v deve ser escalar
    if pd.isna(v):
        return None
    try:
        return float(v)
    except Exception:
        return None


def analyze(news_list):
    resultado_linhas = []
    resumo_por_empresa = {}

    # agrupar por empresa para reduzir downloads repetidos
    noticias_por_empresa = {}
    for item in news_list:
        emp = item.get("empresa", "UNKNOWN")
        noticias_por_empresa.setdefault(emp, []).append(item)

    for empresa, noticias in noticias_por_empresa.items():
        ticker = ticker_for_company(empresa)
        if not ticker:
            print(f"⚠️  Aviso: ticker não encontrado para empresa '{empresa}'. Pulando. (Adicione em TICKER_MAP)")
            continue

        # determinar intervalo global para baixar uma vez por empresa: da menor data - buffer até maior data + buffer
        datas = [to_date(x.get("data_publicacao")) for x in noticias]
        datas = [d for d in datas if d is not None]
        if not datas:
            print(f"⚠️  Nenhuma data válida para {empresa}. Pulando.")
            continue

        min_date = min(datas).date() - timedelta(days=WINDOW_BEFORE + BUFFER_DAYS)
        max_date = max(datas).date() + timedelta(days=WINDOW_AFTER + BUFFER_DAYS)

        print(f"🔁 Baixando preços para {empresa} ({ticker}) de {min_date} até {max_date} ...")
        prices = download_prices(ticker, min_date, max_date)
        if prices.empty:
            print(f"❌ Não foi possível obter preços para {ticker}. Pulando empresa.")
            continue

        prices = compute_daily_metrics(prices)

        # para cada notícia, coletar dados para -2,-1,0,1,2 dias
        for item in noticias:
            data_iso = item.get("data_publicacao")
            pub_dt = to_date(data_iso)
            if not pub_dt:
                print(f"  ⚠ notícia sem data: {item.get('titulo','(sem título)')}")
                continue

            linha_base = {
                "empresa": empresa,
                "ticker": ticker,
                "titulo": item.get("titulo"),
                "url": item.get("url"),
                "data_publicacao_iso": data_iso,
                "data_publicacao": pub_dt.date().isoformat()
            }

            # coletar preços para offsets
            for offset in range(-WINDOW_BEFORE, WINDOW_AFTER + 1):
                target_dt = (pub_dt + timedelta(days=offset)).date()
                # encontrar pregão mais próximo para target
                pregiao = nearest_trading_day(prices.index, target_dt)
                key_prefix = f"d{offset:+d}"  # d-2, d-1, d0, d+1, d+2
                if pregiao is None:
                    # sem pregão no período
                    linha_base[f"{key_prefix}_date"] = None
                    linha_base[f"{key_prefix}_open"] = None
                    linha_base[f"{key_prefix}_close"] = None
                    linha_base[f"{key_prefix}_pct_change_prev_close"] = None
                    linha_base[f"{key_prefix}_intraday_pct"] = None
                else:
                    row = prices.loc[pregiao]

                    # Se vier mais de uma linha, pegar a primeira
                    if isinstance(row, pd.DataFrame):
                        if len(row) == 0:
                            linha_base[f"{key_prefix}_date"] = None
                            linha_base[f"{key_prefix}_open"] = None
                            linha_base[f"{key_prefix}_close"] = None
                            linha_base[f"{key_prefix}_pct_change_prev_close"] = None
                            linha_base[f"{key_prefix}_intraday_pct"] = None
                            continue
                        row = row.iloc[0]

                    # Agora row deve ser uma Series
                    linha_base[f"{key_prefix}_date"] = pregiao.date().isoformat()
                    linha_base[f"{key_prefix}_open"] = float(row["Open"])
                    linha_base[f"{key_prefix}_close"] = float(row["Close"])

                    pct_prev = row["pct_change_prev_close"]
                    intraday = row["intraday_pct"]

                    linha_base[f"{key_prefix}_pct_change_prev_close"] = to_float_safe(pct_prev)
                    linha_base[f"{key_prefix}_intraday_pct"] = to_float_safe(intraday)

            resultado_linhas.append(linha_base)

        # resumo por empresa (estatísticas simples)
        df_emp = pd.DataFrame(resultado_linhas)
        emp_rows = df_emp[df_emp["empresa"] == empresa]
        resumo_por_empresa[empresa] = {
            "ticker": ticker,
            "n_noticias": len(noticias),
            # exemplo: média da variação intradiária no dia da notícia (d0_intraday_pct)
            "mean_intraday_d0": emp_rows["d+0_intraday_pct"].dropna().mean() if "d+0_intraday_pct" in emp_rows.columns else None,
            "mean_pctchange_d0": emp_rows["d+0_pct_change_prev_close"].dropna().mean() if "d+0_pct_change_prev_close" in emp_rows.columns else None
        }

    # salvar resultados
    df_result = pd.DataFrame(resultado_linhas)
    ensure_output_folder()
    if not df_result.empty:
        df_result.to_csv(OUTPUT_PER_NEWS_CSV, index=False, encoding="utf-8-sig", sep=";")
        print(f"\n💾 Salvo CSV por notícia: {OUTPUT_PER_NEWS_CSV}")
    else:
        print("\n⚠️ Nenhum resultado gerado (df vazio).")

    # resumo por empresa
    resumo_df = pd.DataFrame([
        {"empresa": k, **v} for k, v in resumo_por_empresa.items()
    ])
    if not resumo_df.empty:
        resumo_df.to_csv(OUTPUT_BY_COMPANY_CSV, index=False, encoding="utf-8-sig", sep=";")
        print(f"💾 Salvo resumo por empresa: {OUTPUT_BY_COMPANY_CSV}")

    return df_result, resumo_df


def main():
    print("📌 Iniciando passo 2 — Análise de Dados Financeiros")
    if not os.path.exists(INPUT_NEWS_FILE):
        print(f"❌ Arquivo de notícias não encontrado: {INPUT_NEWS_FILE}")
        print("   Gere o arquivo usando seu pipeline de coleta/processamento (ex.: 02_process_raw.py e 03_export_csv.py).")
        return

    news = load_news(INPUT_NEWS_FILE)
    print(f"ℹ️  Notícias carregadas: {len(news)} (arquivo: {INPUT_NEWS_FILE})")

    df_result, df_resumo = analyze(news)

    print("\n✅ Processamento concluído.")


if __name__ == "__main__":
    main()