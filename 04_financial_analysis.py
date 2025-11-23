#!/usr/bin/env python3
# 04_financial_analysis.py
"""
Análise de Dados Financeiros (Passo 2) para o trabalho.

Dependências:
  - yfinance, pandas, numpy, python-dateutil

Uso:
  python 04_financial_analysis.py

Observação:
  - Leitura de notícias fixa: utiliza apenas pipeline_output/01_03/noticias_processadas_15.json
    (as 15 notícias por empresa já devem ter sido geradas pelo passo anterior).
  - Não há fallback para outras fontes de notícias.
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
# Saídas de 04 devem ficar em uma pasta separada
OUTPUT_FOLDER = "pipeline_output/04_fetch"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Input fixo: apenas as 15 notícias já filtradas
INPUT_NEWS_FILE = os.path.join("pipeline_output", "01_03", "noticias_processadas_15.json")

OUTPUT_PER_NEWS_CSV = os.path.join(OUTPUT_FOLDER, "noticias_com_precos.csv")

# Mapeamento empresa -> ticker B3 (modifique conforme suas empresas)
TICKER_MAP = {
    "Intelbras": "INTB3.SA",
    "TOTVS": "TOTS3.SA",
    "Positivo Tecnologia": "POSI3.SA",
    "Locaweb": "LWSA3.SA",
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
    return data


def to_date(dt_iso):
    if not dt_iso:
        return None
    try:
        return parser.isoparse(dt_iso)
    except Exception:
        try:
            return datetime.fromisoformat(dt_iso.replace("Z", ""))
        except Exception:
            return None


def ticker_for_company(company_name):
    if company_name in TICKER_MAP:
        return TICKER_MAP[company_name]
    for k, v in TICKER_MAP.items():
        if k.lower() in company_name.lower() or company_name.lower() in k.lower():
            return v
    return None


def download_prices(ticker, start_date, end_date):
    start = (start_date - timedelta(days=BUFFER_DAYS)).strftime("%Y-%m-%d")
    end = (end_date + timedelta(days=BUFFER_DAYS)).strftime("%Y-%m-%d")
    try:
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    except Exception as e:
        print(f"⚠️ Aviso: falha ao baixar {ticker} entre {start} e {end}: {e}")
        return pd.DataFrame()
    if df is None or df.empty:
        return df
    df.index = pd.to_datetime(df.index)
    return df


def next_trading_day(idx, target_date):
    """Retorna o próximo pregão a partir da data alvo (inclusive)."""
    target = pd.to_datetime(target_date).normalize()
    nxt = idx[idx >= target]
    return nxt.min() if not nxt.empty else None


def nearest_trading_day_corrected(idx, pub_dt):
    """
    Se a notícia for após o fechamento (~16:00 BRT), usar o próximo pregão.
    Caso contrário, usar o pregão do mesmo dia, se existir, senão o próximo.
    """

    cutoff_hour = 16 

    pub_date = pub_dt.date()
    pub_time = pub_dt.time()

    # Se notícia saiu depois do fechamento → usar pregão seguinte
    if pub_time.hour >= cutoff_hour:
        return next_trading_day(idx, pub_date + timedelta(days=1))

    # Caso saia antes → tentar o mesmo dia
    pub_day = pd.to_datetime(pub_date)

    if pub_day in idx:
        return pub_day

    # se não houver pregão no mesmo dia (feriado/fds) → próximo
    return next_trading_day(idx, pub_date)



def compute_daily_metrics(prices_df):
    df = prices_df.copy()
    df["pct_change_prev_close"] = df["Close"].pct_change()
    df["intraday_pct"] = (df["Close"] - df["Open"]) / df["Open"]
    return df


def to_float_safe(v):
    if isinstance(v, pd.Series):
        if v.size == 0:
            return None
        v = v.iloc[0]
    if v is None:
        return None
    if pd.isna(v):
        return None
    try:
        return float(v)
    except Exception:
        return None


def analyze(news_list):
    resultado_linhas = []

    noticias_por_empresa = {}
    for item in news_list:
        emp = item.get("empresa", "UNKNOWN")
        noticias_por_empresa.setdefault(emp, []).append(item)

    for empresa, noticias in noticias_por_empresa.items():
        ticker = ticker_for_company(empresa)
        if not ticker:
            print(f"⚠️  Aviso: ticker não encontrado para empresa '{empresa}'. Pulando.")
            continue

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

        idx = prices.index

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

            # Encontra o pregão-base mais próximo da data de publicação
            base_pregao = nearest_trading_day_corrected(idx, pub_dt)
            if base_pregao is None:
                for offset in range(-WINDOW_BEFORE, WINDOW_AFTER + 1):
                    key = f"d{offset:+d}"
                    linha_base[f"{key}_date"] = None
                    linha_base[f"{key}_open"] = None
                    linha_base[f"{key}_close"] = None
                    linha_base[f"{key}_pct_change_prev_close"] = None
                    linha_base[f"{key}_intraday_pct"] = None
                resultado_linhas.append(linha_base)
                continue

            base_pos = prices.index.get_loc(base_pregao)
            for offset in range(-WINDOW_BEFORE, WINDOW_AFTER + 1):
                day_pos = base_pos + offset
                key_prefix = f"d{offset:+d}"
                if day_pos < 0 or day_pos >= len(prices.index):
                    linha_base[f"{key_prefix}_date"] = None
                    linha_base[f"{key_prefix}_open"] = None
                    linha_base[f"{key_prefix}_close"] = None
                    linha_base[f"{key_prefix}_pct_change_prev_close"] = None
                    linha_base[f"{key_prefix}_intraday_pct"] = None
                    continue

                day_idx = prices.index[day_pos]
                row = prices.iloc[day_pos]
                if isinstance(row, pd.DataFrame) and not row.empty:
                    row = row.iloc[0]

                linha_base[f"{key_prefix}_date"] = day_idx.date().isoformat()
                linha_base[f"{key_prefix}_open"] = float(row["Open"])
                linha_base[f"{key_prefix}_close"] = float(row["Close"])

                pct_prev = row["pct_change_prev_close"]
                intraday = row["intraday_pct"]

                linha_base[f"{key_prefix}_pct_change_prev_close"] = to_float_safe(pct_prev)
                linha_base[f"{key_prefix}_intraday_pct"] = to_float_safe(intraday)

            resultado_linhas.append(linha_base)

        # Observação: não gerar resumo neste script (mantemos apenas o CSV de notícias)
        # If você quiser, remova qualquer trecho de geração de resumo neste bloco.

    df_result = pd.DataFrame(resultado_linhas)
    ensure_output_folder()
    if not df_result.empty:
        df_result.to_csv(OUTPUT_PER_NEWS_CSV, index=False, encoding="utf-8-sig", sep=";")
        print(f"\n💾 Salvo CSV por notícia: {OUTPUT_PER_NEWS_CSV}")
    else:
        print("\n⚠️ Nenhum resultado gerado (df vazio).")

    return df_result


def main():
    print("📌 Iniciando passo 2 — Análise de Dados Financeiros")
    if not os.path.exists(INPUT_NEWS_FILE):
        print(f"❌ Arquivo de notícias não encontrado: {INPUT_NEWS_FILE}")
        print("   Gere o arquivo usando seu pipeline de coleta/processamento (ex.: 02_process_raw.py).")
        return

    news = load_news(INPUT_NEWS_FILE)
    print(f"ℹ️  Notícias carregadas: {len(news)} (arquivo: {INPUT_NEWS_FILE})")

    df_result = analyze(news)
    print("\n✅ Processamento concluído.")


if __name__ == "__main__":
    main()