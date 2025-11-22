#!/usr/bin/env python3
import json
import time
import tls_client
from bs4 import BeautifulSoup
from collections import defaultdict
import os

# Diretório consolidado 01_03 (somente RAW)
BASE_OUT_01_03 = "pipeline_output/01_03"
os.makedirs(BASE_OUT_01_03, exist_ok=True)

# Arquivo de saída RAW (não processado ainda)
RAW_OUTPUT = os.path.join(BASE_OUT_01_03, "raw_infomoney.json")

# tag_id de Intelbras (substitua pelo valor real)
INTB3_TAG_ID = 9999  # substitua pelo tag_id real para Intelbras

# Atualiza o mapeamento para incluir Intelbras
EMPRESAS = {
    "TOTVS": 2309,
    "Positivo Tecnologia": 2702,
    "Locaweb": 1742,
    "Intelbras": 171631
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "Origin": "https://www.infomoney.com.br"
}

client = tls_client.Session(
    client_identifier="chrome_120",
    random_tls_extension_order=True
)

print("\n🚀 Iniciando coleta RAW...\n")

resultado_final = {}

for empresa, tag_id in EMPRESAS.items():
    print(f"📌 Coletando: {empresa} (tag {tag_id})")

    payload = {
        "post_id": 2784666,
        "categories": [],
        "tags": [tag_id],
        "showHat": False
    }

    resposta_empresa = client.post("https://www.infomoney.com.br/wp-json/infomoney/v1/cards", headers=headers, json=payload)

    if resposta_empresa.status_code == 200:
        dados = resposta_empresa.json()
        resultado_final[empresa] = dados
        print(f"✔ {len(dados)} registros coletados\n")
    else:
        print(f"❌ Erro {resposta_empresa.status_code}: não foi possível coletar.\n")
    
    time.sleep(1)

# salvar RAW apenas (_sem processar_)
with open(RAW_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(resultado_final, f, indent=2, ensure_ascii=False)

print(f"\n💾 RAW salvo em: {RAW_OUTPUT}")
print("🎉 Etapa 1 concluída!")