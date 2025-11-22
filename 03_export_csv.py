#!/usr/bin/env python3
"""
03_export_csv.py

Exporta apenas as 15 notícias por empresa a partir do arquivo noticias_processadas.json
gerado em pipeline_output/01_03/noticias_processadas.json.

Saída:
  - pipeline_output/01_03/noticias_processadas_15.json
Não gera nem o resumo nem as notas com preços.
"""

import os
import json
from collections import defaultdict

BASE_OUT = "pipeline_output/01_03"
INPUT_JSON = os.path.join(BASE_OUT, "noticias_processadas.json")
OUTPUT_JSON = os.path.join(BASE_OUT, "noticias_processadas_15.json")

def main():
    if not os.path.exists(INPUT_JSON):
        print(f"Arquivo de noticias não encontrado: {INPUT_JSON}")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Espera-se uma lista de notícias (conforme 02_process_raw.py)
    if not isinstance(data, list):
        print("Formato de dados inesperado: esperado uma lista de notícias.")
        return

    # Mantém a ordem original e coleta até 15 notícias por empresa
    seen = defaultdict(int)
    result = []
    for item in data:
        emp = item.get("empresa", "UNKNOWN")
        if seen[emp] < 15:
            result.append(item)
            seen[emp] += 1

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Salvou 15 notícias por empresa em: {OUTPUT_JSON}")
    print(f"Total de notícias após filtro: {len(result)}")

if __name__ == "__main__":
    main()