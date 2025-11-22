import json
import tls_client
import time

# -------- CONFIG --------

OUTPUT_FILE = "raw_infomoney.json"

# tag_id de cada empresa
EMPRESAS = {
    "TOTVS": 2309,
    "Positivo Tecnologia": 2702,
    "Locaweb": 1742,
    "Sinqia": 2804
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "Origin": "https://www.infomoney.com.br"
}

API_URL = "https://www.infomoney.com.br/wp-json/infomoney/v1/cards"

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

    resposta_empresa = client.post(API_URL, headers=headers, json=payload)

    if resposta_empresa.status_code == 200:
        dados = resposta_empresa.json()
        resultado_final[empresa] = dados
        print(f"✔ {len(dados)} registros coletados\n")
    else:
        print(f"❌ Erro {resposta_empresa.status_code}: não foi possível coletar.\n")
    
    time.sleep(1)

# salvar organizado
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(resultado_final, f, indent=2, ensure_ascii=False)

print("\n💾 RAW salvo em:", OUTPUT_FILE)
print("🎉 Etapa 1 concluída!")
