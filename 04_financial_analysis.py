#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
from dateutil import parser
import pandas as pd
import yfinance as yf
import os

# ---------- CONFIG ----------

OUTPUT_FOLDER = "pipeline_output/04_fetch"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

INPUT_NEWS_FILE = os.path.join("pipeline_output", "01_03", "noticias_processadas_15.json")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "noticias_com_precos_civis.csv")

TICKER_MAP = {
    "Intelbras": "INTB3.SA",
    "TOTVS": "TOTS3.SA",
    "Positivo Tecnologia": "POSI3.SA",
    "Locaweb": "LWSA3.SA",
}

WINDOW_BEFORE = 2
WINDOW_AFTER = 2
BUFFER_DAYS = 30  # mantém uma margem grande para pegar dados históricos


# ---------- FUNÇÕES AUXILIARES ----------

def load_news(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def to_date(dt_iso):
    try:
        return parser.isoparse(dt_iso)
    except:
        return None


def ticker_for_company(company_name):
    for k, v in TICKER_MAP.items():
        if k.lower() in company_name.lower():
            return v
    return None


def download_prices(ticker, start_date, end_date):
    start = (start_date - timedelta(days=BUFFER_DAYS)).strftime("%Y-%m-%d")
    end = (end_date + timedelta(days=BUFFER_DAYS)).strftime("%Y-%m-%d")

    df = yf.download(ticker, start=start, end=end, progress=False)

    if df.empty:
        return df

    df.index = pd.to_datetime(df.index).date
    df["pct_change_prev_close"] = df["Close"].pct_change()
    df["intraday_pct"] = (df["Close"] - df["Open"]) / df["Open"]
    return df


def get_last_valid_price(df, target_date):
    """Retorna o preço mais recente ANTERIOR ou do próprio dia. 
       Se não houver, retorna None.
    """
    if hasattr(target_date, "date"):
        target_date = target_date.date()

    valid_dates = df.index[df.index <= target_date]

    if not valid_dates.any():
        return None, None  # sem valores ainda
    
    closest = valid_dates[-1]
    return df.loc[closest], closest


# ---------- PROCESSAMENTO PRINCIPAL ----------

def analyze(news_list):
    resultados = []

    for empresa, grupo in pd.DataFrame(news_list).groupby("empresa"):
        ticker = ticker_for_company(empresa)

        if not ticker:
            print(f"⚠️ Ignorando {empresa}, ticker não encontrado.")
            continue

        datas_publicacao = [to_date(x) for x in grupo["data_publicacao"]]
        datas_publicacao = [d for d in datas_publicacao if d]

        start = min(datas_publicacao).date() - timedelta(days=WINDOW_BEFORE + BUFFER_DAYS)
        end = max(datas_publicacao).date() + timedelta(days=WINDOW_AFTER + BUFFER_DAYS)

        print(f"📈 Baixando preços para {empresa} ({ticker})...")

        prices = download_prices(ticker, start, end)

        for _, linha in grupo.iterrows():
            pub_dt = to_date(linha["data_publicacao"])
            base_date = pub_dt.date()

            registro = {
                "empresa": empresa,
                "ticker": ticker,
                "titulo": linha["titulo"],
                "url": linha["url"],
                "data_publicacao": base_date.isoformat()
            }

            last_valid_price = None
            last_valid_date = None

            for offset in range(-WINDOW_BEFORE, WINDOW_AFTER + 1):
                target_day = base_date + timedelta(days=offset)
                key = f"d{offset:+d}"

                price_info, real_price_date = get_last_valid_price(prices, target_day)

                registro[f"{key}_date"] = target_day.isoformat()

                # Determinar se houve pregão no dia:
                no_pregao = (real_price_date != target_day)
                registro[f"{key}_no_pregao"] = bool(no_pregao)

                if price_info is not None:
                    last_valid_price = price_info
                    last_valid_date = real_price_date

                if last_valid_price is not None:
                    registro[f"{key}_open"] = float(last_valid_price["Open"])
                    registro[f"{key}_close"] = float(last_valid_price["Close"])
                    registro[f"{key}_pct_change_prev_close"] = float(last_valid_price.get("pct_change_prev_close", 0))
                    registro[f"{key}_intraday_pct"] = float(last_valid_price.get("intraday_pct", 0))
                else:
                    registro[f"{key}_open"] = None
                    registro[f"{key}_close"] = None
                    registro[f"{key}_pct_change_prev_close"] = None
                    registro[f"{key}_intraday_pct"] = None

            resultados.append(registro)

    df = pd.DataFrame(resultados)
    df.to_csv(OUTPUT_FILE, index=False, sep=";", encoding="utf-8-sig")

    print(f"\n💾 Arquivo salvo:\n   {OUTPUT_FILE}")
    return df


# ---------- EXECUÇÃO ----------

if __name__ == "__main__":
    print("\n🚀 Iniciando análise (dias civis + flag de pregão)...\n")
    
    if os.path.exists(INPUT_NEWS_FILE):
        analyze(load_news(INPUT_NEWS_FILE))
        print("\n✅ Finalizado com sucesso!")
    else:
        print(f"❌ Arquivo de entrada não encontrado: {INPUT_NEWS_FILE}")
